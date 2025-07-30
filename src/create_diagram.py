import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx
from pathlib import Path
import math
import json

def create_diagram(input_path):
    """
    Create a visual diagram of the text processing pipeline using Plotly and NetworkX.
    Includes content previews at each stage.
    Saves the diagram as an HTML file in the output directory.
    """
    
    # Read the input file and generated outputs
    base = Path(input_path).stem
    out_dir = Path("data/outputs")
    
    # Helper function to truncate text for preview
    def truncate_text(text, max_length=100):
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    # Read input text
    try:
        input_text = Path(input_path).read_text(encoding="utf-8")
        input_preview = truncate_text(input_text)
    except:
        input_preview = "Input text file"
    
    # Read corrections if available
    corrections_preview = "No corrections found"
    try:
        corrections_file = out_dir / f"{base}_corrections.json"
        if corrections_file.exists():
            with open(corrections_file, 'r', encoding='utf-8') as f:
                corrections = json.load(f)
            if corrections:
                corrections_preview = f"Found {len(corrections)} corrections"
                if len(corrections) > 0:
                    first_correction = corrections[0]
                    corrections_preview += f"\nExample: '{first_correction.get('original', '')}' → '{first_correction.get('corrected', '')}'"
    except:
        pass

    # Read corrected text preview (NEW)
    corrected_preview = "Corrected text file"
    try:
        corrected_file = out_dir / f"{base}_corrected.txt"
        if corrected_file.exists():
            corrected_text = corrected_file.read_text(encoding='utf-8')
            corrected_preview = truncate_text(corrected_text)
    except:
        pass
    
    # Read style outputs
    style_previews = {}
    styles = ['academic', 'simple', 'children']
    for style in styles:
        try:
            style_file = out_dir / f"{base}_{style}.txt"
            if style_file.exists():
                style_text = style_file.read_text(encoding='utf-8')
                style_previews[style] = truncate_text(style_text)
            else:
                style_previews[style] = f"{style.title()} style output"
        except:
            style_previews[style] = f"{style.title()} style output"
    
    # Read readability scores
    readability_preview = "Readability scores"
    try:
        readability_file = out_dir / f"{base}_readability.json"
        if readability_file.exists():
            with open(readability_file, 'r', encoding='utf-8') as f:
                scores = json.load(f)
            readability_preview = "Readability Scores:\n"
            for style, score_data in scores.items():
                if isinstance(score_data, dict) and 'flesch_reading_ease' in score_data:
                    readability_preview += f"{style.title()}: {score_data['flesch_reading_ease']:.1f}\n"
    except:
        pass
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Define nodes with their properties and previews
    nodes = {
        'input_text': {
            'label': f'Input Text File\n({Path(input_path).name})',
            'color': '#3498db',
            'size': 25,
            'pos': (0, 4),
            'preview': input_preview
        },
        'preprocessor': {
            'label': 'Text Preprocessor\n(Grammar Check)',
            'color': '#e74c3c',
            'size': 20,
            'pos': (2, 4),
            'preview': 'Analyzes text for grammar errors using LanguageTool/llm'
        },
        'corrections_json': {
            'label': 'Corrections JSON\n(Grammar Errors)',
            'color': '#f39c12',
            'size': 15,
            'pos': (4, 5),
            'preview': corrections_preview
        },
        'corrected_text': {
            'label': 'Corrected Text',
            'color': '#2ecc71',
            'size': 20,
            'pos': (4, 3),
            'preview': corrected_preview
        },
        'style_transformer': {
            'label': 'Style Transformer',
            'color': '#9b59b6',
            'size': 20,
            'pos': (6, 3),
            'preview': 'Transforms text into different writing styles using AI model'
        },
        'academic_style': {
            'label': 'Academic Style\n(.txt file)',
            'color': '#34495e',
            'size': 15,
            'pos': (8, 4.5),
            'preview': style_previews['academic']
        },
        'simple_style': {
            'label': 'Simple Style\n(.txt file)',
            'color': '#34495e',
            'size': 15,
            'pos': (8, 3),
            'preview': style_previews['simple']
        },
        'children_style': {
            'label': 'Child-Friendly Style\n(.txt file)',
            'color': '#34495e',
            'size': 15,
            'pos': (8, 1.5),
            'preview': style_previews['children']
        },
        'readability_analyzer': {
            'label': 'Readability Analyzer',
            'color': '#16a085',
            'size': 20,
            'pos': (10, 3),
            'preview': 'Calculates Flesch Reading Ease, FKGL, and other readability metrics'
        },
        'readability_scores': {
            'label': 'Readability Scores\n(.json file)',
            'color': '#f39c12',
            'size': 15,
            'pos': (12, 3),
            'preview': readability_preview
        }
    }
    
    # Add nodes to graph
    for node_id, props in nodes.items():
        G.add_node(node_id, **props)
    
    # Define edges (connections between nodes)
    edges = [
        ('input_text', 'preprocessor'),
        ('preprocessor', 'corrections_json'),
        ('preprocessor', 'corrected_text'),
        ('corrected_text', 'style_transformer'),
        ('style_transformer', 'academic_style'),
        ('style_transformer', 'simple_style'),
        ('style_transformer', 'children_style'),
        ('academic_style', 'readability_analyzer'),
        ('simple_style', 'readability_analyzer'),
        ('children_style', 'readability_analyzer'),
        ('readability_analyzer', 'readability_scores')
    ]
    
    # Add edges to graph
    G.add_edges_from(edges)
    
    # Create hover text with previews
    hover_texts = []
    for node in G.nodes():
        node_data = nodes[node]
        hover_text = f"<b>{node_data['label']}</b><br><br>"
        hover_text += f"<i>Preview:</i><br>{node_data['preview']}"
        hover_texts.append(hover_text)
    
    # Extract node positions and properties for Plotly
    node_trace = go.Scatter(
        x=[nodes[node]['pos'][0] for node in G.nodes()],
        y=[nodes[node]['pos'][1] for node in G.nodes()],
        mode='markers+text',
        text=[nodes[node]['label'] for node in G.nodes()],
        textposition='middle center',
        textfont=dict(size=10, color='black'),
        marker=dict(
            size=[nodes[node]['size'] for node in G.nodes()],
            color=[nodes[node]['color'] for node in G.nodes()],
            line=dict(width=2, color='white'),
            opacity=0.9
        ),
        hoverinfo='text',
        hovertext=hover_texts,
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="black",
            font_size=12,
            font_family="Arial"
        ),
        name='Process Steps'
    )
    
    # Create edge traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = nodes[edge[0]]['pos']
        x1, y1 = nodes[edge[1]]['pos']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color='#7f8c8d'),
        hoverinfo='none',
        mode='lines',
        name='Process Flow'
    )
    
    # Create arrow annotations for better flow visualization
    annotations = []
    for edge in G.edges():
        x0, y0 = nodes[edge[0]]['pos']
        x1, y1 = nodes[edge[1]]['pos']
        
        # Calculate arrow position (slightly before the target node)
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx**2 + dy**2)
        
        # Position arrow 80% along the edge
        arrow_x = x0 + 0.8 * dx
        arrow_y = y0 + 0.8 * dy
        
        annotations.append(
            dict(
                x=arrow_x,
                y=arrow_y,
                ax=x0 + 0.6 * dx,
                ay=y0 + 0.6 * dy,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#7f8c8d'
            )
        )
    
    # Add instruction annotation
    annotations.append(
        dict(
            x=0.02,
            y=0.98,
            xref='paper',
            yref='paper',
            text="<b>💡 Hover over nodes to see content previews</b>",
            showarrow=False,
            font=dict(size=14, color='#2c3e50'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#bdc3c7',
            borderwidth=1
        )
    )
    
    # Create the figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text='Text Processing Pipeline Flow - Interactive Preview',
                x=0.5,
                font=dict(size=20, color='#2c3e50')
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=60),
            annotations=annotations,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1, 13]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0.5, 5.5]
            ),
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color="#2c3e50")
        )
    )
    
    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the diagram as HTML
    output_file = out_dir / f"{base}_pipeline_diagram.html"
    
    # Generate the full HTML with Plotly
    fig_html = fig.to_html(include_plotlyjs='cdn')
    
    # Insert custom styling and header into the generated HTML
    custom_css = '''
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        .info-box {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .legend {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        .legend-item {
            display: flex;
            align-items: center;
            background: white;
            padding: 8px 12px;
            border-radius: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .plotly-graph-div {
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    '''
    
    custom_header = f'''
    <div class="header">
        <h1>📊 Text Processing Pipeline Visualization</h1>
        <p>File: {Path(input_path).name} | Interactive Flow Diagram with Content Previews</p>
    </div>
    
    <div class="info-box">
        <h3>🔍 How to Use This Diagram:</h3>
        <ul>
            <li><strong>Hover over any node</strong> to see content previews and details</li>
            <li><strong>Follow the arrows</strong> to understand the processing flow</li>
            <li><strong>Each color</strong> represents a different type of process or output</li>
        </ul>
    </div>
    
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background-color: #3498db;"></div>Input Files</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #e74c3c;"></div>Text Processing</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #9b59b6;"></div>Style Transformation</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #34495e;"></div>Output Files</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #f39c12;"></div>JSON Data</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #16a085;"></div>Analysis</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #2ecc71;"></div>Processed Text</div>
    </div>
    '''
    
    # Insert custom content into the generated HTML
    final_html = fig_html.replace('<head>', f'<head>{custom_css}')
    final_html = final_html.replace('<body>', f'<body>{custom_header}')
    
    # Save the enhanced HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"📊 Interactive pipeline diagram with previews saved to: {output_file}")
    print("💡 Open the HTML file in your browser and hover over nodes to see content previews!")
    
    return str(output_file)

if __name__ == "__main__":
    # Example usage
    create_diagram("data/input_texts/example.txt")