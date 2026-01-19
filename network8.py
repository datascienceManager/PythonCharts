

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("Cohort Network")

# ---------------------------
# Load CSV
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "networkdata.csv")
df = pd.read_csv(csv_path)

# Build nodes and clusters
node_ids = list(set(df["source"]).union(set(df["target"])))
nodes = []
for n in node_ids:
    cluster = ord(n[0].upper()) % 10
    nodes.append({"id": n, "group": cluster})

links = [{"source": r["source"], "target": r["target"]} for _, r in df.iterrows()]
graph = {"nodes": nodes, "links": links}
graph_json = json.dumps(graph)

# ---------------------------
# HTML content with JS selection inside HTML
# ---------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  body {{ margin: 0; background: #000; }}
  .link {{ stroke: #888; stroke-opacity: 0.4; stroke-width: 1.5px; }}
  .node circle {{
    stroke: #fff;
    stroke-width: 1.5px;
    filter: url(#glow);
    cursor: pointer;
  }}
  .node text {{
    font-family: Arial, sans-serif;
    font-size: 18px;
    font-weight: 600;
    fill: #fff;
    pointer-events: none;
    text-shadow: 1px 1px 2px #000000aa;
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

// Pastel palette
const pastelColors = ["#A8D5BA","#FFD6A5","#FFAAA6","#A0CED9","#FFC3A0","#D5AAFF","#B5EAD7","#FFDAC1","#E2F0CB","#C7CEEA"];
const color = d3.scaleOrdinal(pastelColors);

// Zoom & Pan
const zoomLayer = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.2,5]).on("zoom", event => {{
    zoomLayer.attr("transform", event.transform);
}}));

// Force Simulation
const simulation = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id).distance(120).strength(0.8))
  .force("charge", d3.forceManyBody().strength(-600))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide().radius(45));



// Links

const link = zoomLayer.append("g")
  .selectAll("line")
  .data(graph.links)
  .enter()
  .append("line")
  .attr("class","link")
  .attr("stroke","#888")
  .attr("stroke-opacity", 0.4)
  .attr("stroke-width", 3) ;  // <-- default thickness (was 1.5)

// Nodes
const node = zoomLayer.append("g")
  .selectAll("g")
  .data(graph.nodes)
  .enter()
  .append("g")
  .attr("class","node")
  .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

node.append("circle")
  .attr("r", 20)
  .attr("fill", d => color(d.group));

node.append("text")
  .attr("x", 26)
  .attr("y", 6)
  .text(d => d.id);


// Highlight function
function highlight(selectionNode, selectionGroup) {{{{
    // Nodes
    node.select("circle")
        .transition().duration(300)  // smooth animation
        .attr("r", d => (!selectionNode || d.id === selectionNode || d.group === selectionGroup ? 30 : 15))
        .attr("fill", d => {{{{
            if(!selectionNode || d.id === selectionNode || d.group === selectionGroup) {{{{
                return color(d.group);
            }}}} else {{{{
                return "#555";
            }}}}
        }}}})
        .attr("opacity", d => (!selectionNode || d.id === selectionNode || d.group === selectionGroup ? 1 : 0.2));

    node.select("text")
        .transition().duration(300)
        .attr("opacity", d => (!selectionNode || d.id === selectionNode || d.group === selectionGroup ? 1 : 0.2));

    // Links
    link.transition().duration(300)
        .attr("stroke-width", d => {{
            if(!selectionNode || d.source.id === selectionNode || d.source.group === selectionGroup || 
               d.target.id === selectionNode || d.target.group === selectionGroup) {{{{
                return 6;  // thicker for highlighted links
            }}}} else {{{{
                return 1;  // thin for dimmed links
            }}}}
        }})
        .attr("opacity", d => {{
            if(!selectionNode || d.source.id === selectionNode || d.source.group === selectionGroup || 
               d.target.id === selectionNode || d.target.group === selectionGroup) {{{{
                return 0.8;
            }}}} else {{{{
                return 0.05;
            }}}}
        }});
}}}}




// Reset selection when clicking on empty background
svg.on("click", function(event) {{{{
    if(event.target.tagName === 'svg') {{
        highlight(null, null);
    }}
}}}});

// Click node to highlight its group
node.on("click", function(event, d) {{{{
    event.stopPropagation();  // prevent svg background click
    highlight(d.id, d.group);
    console.log(`Node: ${{d.id}}, Group: ${{d.group}}`);
}}}});

// Tick
simulation.on("tick", () => {{
    link.attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
        .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);
    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

// Drag functions
function dragstarted(event,d){{ if(!event.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }}
function dragged(event,d){{ d.fx=event.x; d.fy=event.y; }}
function dragended(event,d){{ if(!event.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; }}

</script>
</body>
</html>
"""

components.html(html_content, height=700)



# ===== link tickness edges ======

# // Links
# const link = zoomLayer.append("g")
#   .selectAll("line")
#   .data(graph.links)
#   .enter()
#   .append("line")
#   .attr("class","link");

# ===== highlight: previous code =====


# // Highlight function

# function highlight(selectionNode, selectionGroup) {{{{
#     node.select("circle")
#         .attr("fill", d => {{{{
#             if(!selectionNode || d.id === selectionNode || d.group === selectionGroup) {{{{
#                 return color(d.group);
#             }}}} else {{{{
#                 return "#555";
#             }}}}
#         }}}})
#         .attr("opacity", d => (!selectionNode || d.id === selectionNode || d.group === selectionGroup ? 1 : 0.2));

#     node.select("text")
#         .attr("opacity", d => (!selectionNode || d.id === selectionNode || d.group === selectionGroup ? 1 : 0.2));

#     link.attr("opacity", d => {{{{
#         if(!selectionNode || d.source.id === selectionNode || d.source.group === selectionGroup || 
#            d.target.id === selectionNode || d.target.group === selectionGroup) {{{{
#             return 0.8;
#         }}}} else return 0.05;
#     }}}});
# }}}}




# =========== Previous code (network8.py) =============

# import streamlit as st
# import streamlit.components.v1 as components
# import pandas as pd
# import json
# import os

# st.set_page_config(layout="wide")
# st.title("Interactive Glossy Network Graph with Cluster Highlight")

# # ---------------------------
# # Load CSV
# # ---------------------------
# BASE_DIR = os.path.dirname(__file__)
# csv_path = os.path.join(BASE_DIR, "networkdata.csv")

# df = pd.read_csv(csv_path)

# # ---------------------------
# # Build nodes with group
# # ---------------------------
# node_ids = list(set(df["source"]).union(set(df["target"])))
# nodes = []

# # Assign clusters based on first letter for demo
# for n in node_ids:
#     cluster = ord(n[0].upper()) % 10
#     nodes.append({"id": n, "group": cluster})

# links = [{"source": r["source"], "target": r["target"]} for _, r in df.iterrows()]
# graph = {"nodes": nodes, "links": links}
# graph_json = json.dumps(graph)

# # ---------------------------
# # Streamlit widgets
# # ---------------------------
# selected_node = st.selectbox("Select a Node to Highlight", node_ids)
# selected_group = st.selectbox(
#     "Or Select a Cluster to Highlight", sorted(list(set([n['group'] for n in nodes])))
# )

# selection = json.dumps({"node": selected_node, "group": selected_group})

# # ---------------------------
# # Full D3 HTML
# # ---------------------------
# html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <script src="https://d3js.org/d3.v7.min.js"></script>
# <style>
#   body {{ margin: 0; background: #000000; }}
#   .link {{ stroke: #888; stroke-opacity: 0.4; stroke-width: 1.5px; }}
#   .node circle {{
#     stroke: #fff;
#     stroke-width: 1.5px;
#     filter: url(#glow);
#   }}
#   .node text {{
#     font-family: Arial, sans-serif;
#     font-size: 13px;
#     font-weight: 600;
#     fill: #ffffff;
#     pointer-events: none;
#     text-shadow: 1px 1px 2px #000000aa;
#   }}
# </style>
# </head>

# <body>
# <svg width="1200" height="700">
#   <defs>
#     <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
#       <feGaussianBlur stdDeviation="3" result="blur"/>
#       <feMerge>
#         <feMergeNode in="blur"/>
#         <feMergeNode in="SourceGraphic"/>
#       </feMerge>
#     </filter>
#   </defs>
# </svg>

# <script>
# const graph = {graph_json};
# const selection = {selection};
# const width = 1200;
# const height = 700;

# const svg = d3.select("svg");

# // Pastel color palette
# const pastelColors = ["#A8D5BA","#FFD6A5","#FFAAA6","#A0CED9","#FFC3A0","#D5AAFF","#B5EAD7","#FFDAC1","#E2F0CB","#C7CEEA"];
# const color = d3.scaleOrdinal(pastelColors);

# // Zoom & Pan
# const zoomLayer = svg.append("g");
# svg.call(d3.zoom().scaleExtent([0.2,5]).on("zoom", (event) => {{
#     zoomLayer.attr("transform", event.transform);
# }}));

# // Force Simulation
# const simulation = d3.forceSimulation(graph.nodes)
#   .force("link", d3.forceLink(graph.links).id(d => d.id).distance(120).strength(0.8))
#   .force("charge", d3.forceManyBody().strength(-600))
#   .force("center", d3.forceCenter(width/2, height/2))
#   .force("collision", d3.forceCollide().radius(45));

# // Links
# const link = zoomLayer.append("g")
#   .selectAll("line")
#   .data(graph.links)
#   .enter()
#   .append("line")
#   .attr("class","link");

# // Nodes
# const node = zoomLayer.append("g")
#   .selectAll("g")
#   .data(graph.nodes)
#   .enter()
#   .append("g")
#   .attr("class","node")
#   .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

# node.append("circle")
#   .attr("r", 20)
#   .attr("fill", d => color(d.group));

# node.append("text")
#   .attr("x", 26)
#   .attr("y", 6)
#   .text(d => d.id);

# // Highlight function
# function highlight(selectionNode, selectionGroup) {{{{
#     node.select("circle")
#         .attr("fill", d => {{{{
#             if(d.id === selectionNode || d.group == selectionGroup) {{{{
#                 return color(d.group);
#             }}}} else {{{{
#                 return "#555";
#             }}}}
#         }}}})
#         .attr("opacity", d => (d.id === selectionNode || d.group == selectionGroup ? 1 : 0.2));

#     node.select("text")
#         .attr("opacity", d => (d.id === selectionNode || d.group == selectionGroup ? 1 : 0.2));

#     link.attr("opacity", d => {{{{
#         if(d.source.id === selectionNode || d.source.group == selectionGroup || 
#            d.target.id === selectionNode || d.target.group == selectionGroup) {{{{
#             return 0.8;
#         }}}} else return 0.05;
#     }}}});
# }}}}

# // Initial highlight from Streamlit selection
# highlight(selection.node, selection.group);

# // Node click event
# node.on("click", function(event, d) {{{{
#     highlight(d.id, d.group);
#     alert(`Node: ${{d.id}}\\nGroup: ${{d.group}}`);
# }}}});

# // Tick
# simulation.on("tick", () => {{
#     link.attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
#         .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);
#     node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
# }});

# // Drag functions
# function dragstarted(event,d){{ if(!event.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }}
# function dragged(event,d){{ d.fx=event.x; d.fy=event.y; }}
# function dragended(event,d){{ if(!event.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; }}
# </script>
# </body>
# </html>
# """

# # ---------------------------
# # Render in Streamlit
# # ---------------------------
# components.html(html_content, height=700)
