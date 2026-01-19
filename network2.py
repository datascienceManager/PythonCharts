import streamlit as st
import streamlit.components.v1 as components
from d3graph import d3graph, vec2adjmat
import os
import time

st.title("D3 Network Graph")

# Initialize
d3 = d3graph()

# Load energy example
df = d3.import_example('energy')
adjmat = vec2adjmat(source=df['source'], target=df['target'], weight=df['weight'])

# Process adjmat
d3.graph(adjmat)

# Change node properties
d3.set_node_properties(scaler='minmax', color=None)
d3.node_properties['Solar']['size'] = 30
d3.node_properties['Solar']['color'] = '#FF0000'
d3.node_properties['Solar']['edge_color'] = '#000000'
d3.node_properties['Solar']['edge_size'] = 5

# Save to absolute path in current directory
current_dir = os.getcwd()
html_path = os.path.join(current_dir, 'network_graph.html')

st.write(f"Saving to: {html_path}")

# Show and save
d3.show(filepath=html_path, showfig=False)

# Wait for file to be written
time.sleep(1)

# Check if file exists
if os.path.exists(html_path):
    st.success("File created successfully!")
    
    # Read and display the HTML
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Display in Streamlit
    components.html(html_content, height=800, scrolling=True)
else:
    st.error(f"File not found at: {html_path}")
    st.write(f"Current directory: {current_dir}")
    st.write(f"Files in directory: {os.listdir(current_dir)}")