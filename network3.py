import streamlit as st
import streamlit.components.v1 as components
import os
import json

st.set_page_config(layout="wide")
st.title("D3 Network Graph – Single File Streamlit App")

# --------------------------------
# Network data (Python)
# --------------------------------
graph = {
    "nodes": [
        {"id": "A", "group": 1},
        {"id": "B", "group": 1},
        {"id": "C", "group": 2},
        {"id": "D", "group": 2},
        {"id": "E", "group": 3}
    ],
    "links": [
        {"source": "A", "target": "B"},
        {"source": "A", "target": "C"},
        {"source": "B", "target": "D"},
        {"source": "C", "target": "D"},
        {"source": "D", "target": "E"}
    ]
}

graph_json = json.dumps(graph)

# --------------------------------
# Create HTML dynamically
# --------------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  .link {{ stroke: #999; stroke-opacity: 0.6; }}
  text {{ font-family: Arial; font-size: 12px; }}
</style>
</head>

<body>
<svg width="900" height="500"></svg>

<script>
const graph = {graph_json};
const width = 900;
const height = 500;

const svg = d3.select("svg");
const color = d3.scaleOrdinal(d3.schemeCategory10);

const simulation = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id).distance(80))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
  .selectAll("line")
  .data(graph.links)
  .enter()
  .append("line")
  .attr("class", "link");

const node = svg.append("g")
  .selectAll("g")
  .data(graph.nodes)
  .enter()
  .append("g")
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended)
  );

node.append("circle")
  .attr("r", 10)
  .attr("fill", d => color(d.group));

node.append("text")
  .attr("x", 12)
  .attr("y", 3)
  .text(d => d.id);

simulation.on("tick", () => {{
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

function dragstarted(event, d) {{
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}}

function dragged(event, d) {{
  d.fx = event.x;
  d.fy = event.y;
}}

function dragended(event, d) {{
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}}
</script>
</body>
</html>
"""

# --------------------------------
# (Optional) Save HTML locally
# --------------------------------
BASE_DIR = os.path.dirname(__file__)
html_path = os.path.join(BASE_DIR, "network_graph.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# --------------------------------
# Render in Streamlit
# --------------------------------
components.html(html_content, height=550)
