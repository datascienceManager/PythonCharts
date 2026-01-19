import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("Network Diagram from CSV (Source → Target)")

# ---------------------------
# Load CSV
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "networkdata.csv")

df = pd.read_csv(csv_path)

# ---------------------------
# Build nodes and links
# ---------------------------
nodes = set(df["source"]).union(set(df["target"]))

graph = {
    "nodes": [{"id": n, "group": 1} for n in nodes],
    "links": [{"source": r["source"], "target": r["target"]} for _, r in df.iterrows()]
}

graph_json = json.dumps(graph)

# ---------------------------
# D3 HTML
# ---------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  body {{ margin: 0; }}
  .link {{ stroke: #999; stroke-opacity: 0.6; }}
  .node text {{ font-size: 12px; }}
</style>
</head>

<body>
<svg width="1000" height="600"></svg>

<script>
const graph = {graph_json};
const width = 1000;
const height = 600;

const svg = d3.select("svg");
const color = d3.scaleOrdinal(d3.schemeTableau10);

const simulation = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id).distance(90))
  .force("charge", d3.forceManyBody().strength(-350))
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
  .attr("fill", d => color(d.id));

node.append("text")
  .attr("x", 14)
  .attr("y", 4)
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

# ---------------------------
# Render
# ---------------------------
components.html(html_content, height=650)
