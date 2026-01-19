import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("Glossy Light Clustered Network Graph")

# ---------------------------
# Load CSV
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "networkdata.csv")

df = pd.read_csv(csv_path)

# ---------------------------
# Build nodes with group
# ---------------------------
node_ids = list(set(df["source"]).union(set(df["target"])))
nodes = []

# Assign clusters based on first letter for demo
for n in node_ids:
    cluster = ord(n[0].upper()) % 10
    nodes.append({"id": n, "group": cluster})

links = [{"source": r["source"], "target": r["target"]} for _, r in df.iterrows()]
graph = {"nodes": nodes, "links": links}
graph_json = json.dumps(graph)

# ---------------------------
# D3 HTML with pastel glossy nodes
# ---------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  body {{ margin: 0; background: #000000; }}
  .link {{ stroke: #999; stroke-opacity: 0.4; stroke-width: 1.5px; }}
  .node circle {{
    stroke: #fff;
    stroke-width: 1.5px;
    filter: url(#glow);  /* glow effect */
  }}
  .node text {{
    font-family: Arial, sans-serif;
    font-size: 13px;
    font-weight: 600;
    fill: #ffffff;
    pointer-events: none;
    text-shadow: 1px 1px 2px #00000066;
  }}
</style>
</head>

<body>
<svg width="1200" height="700">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
</svg>

<script>
const graph = {graph_json};
const width = 1200;
const height = 700;

const svg = d3.select("svg");

// -------------------------------
// Pastel color palette for clusters
// -------------------------------
const pastelColors = [
  "#A8D5BA","#FFD6A5","#FFAAA6","#A0CED9","#FFC3A0",
  "#D5AAFF","#B5EAD7","#FFDAC1","#E2F0CB","#C7CEEA"
];
const color = d3.scaleOrdinal(pastelColors);

// -------------------------------
// Zoom & Pan
// -------------------------------
const zoomLayer = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.2,5]).on("zoom", (event) => {{
  zoomLayer.attr("transform", event.transform);
}}));

// -------------------------------
// Force Simulation
// -------------------------------
const simulation = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id).distance(120).strength(0.8))
  .force("charge", d3.forceManyBody().strength(-600))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide().radius(45));

// -------------------------------
// Links
// -------------------------------
const link = zoomLayer.append("g")
  .selectAll("line")
  .data(graph.links)
  .enter()
  .append("line")
  .attr("class","link");

// -------------------------------
// Nodes
// -------------------------------
const node = zoomLayer.append("g")
  .selectAll("g")
  .data(graph.nodes)
  .enter()
  .append("g")
  .attr("class","node")
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended)
  );

node.append("circle")
  .attr("r", 20)
  .attr("fill", d => color(d.group));

node.append("text")
  .attr("x", 26)
  .attr("y", 6)
  .text(d => d.id);

// -------------------------------
// Tick
// -------------------------------
simulation.on("tick", () => {{
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

// -------------------------------
// Drag functions
// -------------------------------
function dragstarted(event, d) {{
  if(!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}}

function dragged(event,d){{
  d.fx = event.x;
  d.fy = event.y;
}}

function dragended(event,d){{
  if(!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}}
</script>
</body>
</html>
"""

# ---------------------------
# Render in Streamlit
# ---------------------------
components.html(html_content, height=700)
