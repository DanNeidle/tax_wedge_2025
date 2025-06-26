import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import plotly.io as pio
import base64

# Set default Plotly template for a cleaner look
pio.templates.default = "plotly_white"

# 1. Read the data -----------------------------------------------------------
# Please ensure this file path is correct and accessible.
FILE = Path("/Users/dan/Dan/tax policy associates/OECD personal tax comparisons 2025.xlsx")
SHEET = "Tax wedges 2024"


# Define colors
single_worker_color = "rgba(100, 149, 237, 0.9)" # Cornflower Blue
family_two_earners_color = "rgba(255, 99, 71, 0.9)"        # Tomato
family_single_earner_color = "rgba(255, 165, 0, 0.9)" # Orange for new data
connector_color = "gray"
highlight_color = "red"

# Only the first four columns are needed (A-D)
cols = "A:D"
df = (
    pd.read_excel(FILE, sheet_name=SHEET, usecols=cols)
      .iloc[:, [0, 1, 2, 3]]               # Now include column 2 (index 2) for single-earner family
      .dropna()
)

# Rename columns for easier access and clarity in Plotly
df.columns = ["Country", "single_worker", "family_single_earner", "family_two_earners"]

num_countries = len(df)

# Pre-compute sorted data for each sorting option
sorted_data = {}
sort_columns_list = ["single_worker", "family_single_earner", "family_two_earners"]

for col_name in sort_columns_list:
    df_sorted = df.sort_values(col_name, ascending=False).reset_index(drop=True)

    trace_x_values = []
    trace_y_values = []
    trace_line_colors = [] # For connector traces
    trace_line_widths = [] # For connector traces
    
    # Generate data for connector lines (N individual traces) and their styles
    for i, row in df_sorted.iterrows():
        trace_x_values.append([row["single_worker"], row["family_single_earner"], row["family_two_earners"]])
        trace_y_values.append([row["Country"], row["Country"], row["Country"]])
        
        # Determine line style based on country for this sorted order
        line_color = highlight_color if row["Country"] == "United Kingdom" else connector_color
        line_width = 3 if row["Country"] == "United Kingdom" else 1.5
        trace_line_colors.append(line_color)
        trace_line_widths.append(line_width)

    # Generate data for point traces
    # Ensure these are appended in the same order as they will be added to the figure
    trace_x_values.append(df_sorted["single_worker"].tolist()) # Single worker
    trace_y_values.append(df_sorted["Country"].tolist())
    trace_line_colors.append(None) # No line style for points
    trace_line_widths.append(None)

    trace_x_values.append(df_sorted["family_single_earner"].tolist()) # Single earner family
    trace_y_values.append(df_sorted["Country"].tolist())
    trace_line_colors.append(None)
    trace_line_widths.append(None)

    trace_x_values.append(df_sorted["family_two_earners"].tolist()) # Two earner family
    trace_y_values.append(df_sorted["Country"].tolist())
    trace_line_colors.append(None)
    trace_line_widths.append(None)

    # Prepare tick labels for y-axis highlighting
    tick_labels = []
    for country_name in df_sorted["Country"]:
        if country_name == "United Kingdom":
            tick_labels.append(f"<b><span style='color:{highlight_color};'>{country_name}</span></b>")
        else:
            tick_labels.append(country_name)
    
    sorted_data[col_name] = {
        'trace_x_values': trace_x_values,
        'trace_y_values': trace_y_values,
        'trace_line_colors': trace_line_colors,
        'trace_line_widths': trace_line_widths,
        'tick_labels': tick_labels,
        'country_order': df_sorted['Country'].tolist()
    }

# 2. Create the initial plot (e.g., sorted by single_worker) --------------------
initial_sort_column = "single_worker"
initial_data = sorted_data[initial_sort_column]

fig = go.Figure()

# Add traces in the correct order for indexing later in updatemenus
# Connector lines (N traces) - These will be traces 0 to num_countries-1
for i in range(num_countries):
    fig.add_trace(go.Scatter(
        x=initial_data['trace_x_values'][i],
        y=initial_data['trace_y_values'][i],
        mode='lines',
        line=dict(color=initial_data['trace_line_colors'][i], width=initial_data['trace_line_widths'][i]),
        showlegend=False, 
        hoverinfo='skip'  
    ))

# Add point traces (3 traces) - these are at indices num_countries, num_countries+1, num_countries+2
fig.add_trace(go.Scatter(
    x=initial_data['trace_x_values'][num_countries], # Single worker
    y=initial_data['trace_y_values'][num_countries],
    mode='markers',
    marker=dict(
        symbol='circle',
        size=10,
        color=single_worker_color,
        line=dict(width=0.5, color='DarkSlateGrey')
    ),
    name='Single worker',
    hovertemplate='%{x:.1%}'
))

fig.add_trace(go.Scatter(
    x=initial_data['trace_x_values'][num_countries + 1], # Single-earner family
    y=initial_data['trace_y_values'][num_countries + 1],
    mode='markers',
    marker=dict(
        symbol='diamond',
        size=10,
        color=family_single_earner_color,
        line=dict(width=0.5, color='DarkSlateGrey')
    ),
    name='Single-earner family',
    hovertemplate='%{x:.1%}'
))

fig.add_trace(go.Scatter(
    x=initial_data['trace_x_values'][num_countries + 2], # Two-earner family
    y=initial_data['trace_y_values'][num_countries + 2],
    mode='markers',
    marker=dict(
        symbol='square',
        size=10,
        color=family_two_earners_color,
        line=dict(width=0.5, color='DarkSlateGrey')
    ),
    name='Two-earner family',
    hovertemplate='%{x:.1%}'
))


# 3. Layout and interactive elements -----------------------------------------
fig.update_layout(
    height=20 * num_countries + 200, # Adjust height based on number of countries
    title=dict(
        text="<b>% of wages paid in tax for the average worker across the OECD</b>",
        font=dict(size=24),
        x=0.5, # Center title
        xanchor='center'
    ),
    xaxis_title=dict(
        text="Tax wedge - all employment taxes as % of labour cost - see article for details",
        font=dict(size=16)
    ),
    yaxis=dict(
        autorange="reversed", # Invert y-axis to match original
        tickfont=dict(size=16), # Increased country name font size
        title_standoff=10, # Add some space between y-axis label and ticks
        tickmode='array',
        tickvals=initial_data['country_order'], # Set initial tickvals
        ticktext=initial_data['tick_labels'], # Set initial ticktext
    ),
    xaxis=dict(
        gridcolor='lightgrey',
        showgrid=True,
        griddash='dash',
        zeroline=False,
        tickfont=dict(size=14),
        tickformat=".0%",  # Format as percentage with 0 decimal places
        dtick=0.05,         # Ticks every 0.05 (which is 5%)
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="center",
        x=0.5,
        font=dict(size=18),
        bgcolor='rgba(255,255,255,0)',
        bordercolor='rgba(255,255,255,0)',
        traceorder='reversed',
    ),
    hovermode="y unified",
    margin=dict(l=150, r=50, t=100, b=100),
    plot_bgcolor='white',
    font=dict(
        family="Arial",
        size=12,         # Default size for most text
        color="black"    # Default color
    ),
    annotations=[
        dict(
            text="Source: OECD Taxing Wages report, 2025",
            xref="paper",  # Refer to the plotting area itself
            yref="paper",  # Refer to the plotting area itself
            x=1,           # Position at the right edge of the plot
            y=-0.05,       # Position below the x-axis, adjust as needed
            showarrow=False, # No arrow for a simple text annotation
            font=dict(
                size=11,   
            ),
            xanchor="right", # Anchor the text to its right side at x=1
            yanchor="top"    # Anchor the text to its top side at y=-0.15
        ),
    ],
)

# Create buttons for the dropdown menu
buttons = []
for sort_col_name in sort_columns_list:
    data_for_button = sorted_data[sort_col_name]
    button_label = sort_col_name.replace("_", " ").title() # E.g., "Single Worker"

    # Create lists of updates for 'x', 'y', 'line.color', 'line.width' for all traces
    # These lists must match the order of traces added to the figure.
    x_updates = data_for_button['trace_x_values']
    y_updates = data_for_button['trace_y_values']
    line_color_updates = data_for_button['trace_line_colors']
    line_width_updates = data_for_button['trace_line_widths']

    button = dict(
        label=button_label,
        method="update", # 'update' allows applying both restyle (trace data) and relayout (layout data)
        args=[
            # restyle arguments (what to update in traces)
            {
                'x': x_updates,
                'y': y_updates,
                'line.color': line_color_updates,
                'line.width': line_width_updates
            },
            # relayout arguments (what to update in layout)
            {
                'yaxis.ticktext': data_for_button['tick_labels'],
                'yaxis.tickvals': data_for_button['country_order'],
                'yaxis.autorange': "reversed" # Ensure it remains reversed after update
            }
        ]
    )
    buttons.append(button)

# Create the "Toggle Connectors" button
# The indices for connector traces are from 0 to num_countries - 1
connector_trace_indices = list(range(num_countries))

toggle_connectors_button = dict(
    type="buttons",
    direction="right", # Or "up" if you want it vertically aligned
    x=0.84, # Position the button, adjust as needed
    xanchor="left",
    y=0.13, # Position the button, adjust as needed (below the dropdown)
    yanchor="bottom",
    buttons=[
        dict(
            label="Toggle Connectors",
            method="restyle",
            args=[
                {'visible': [False] * num_countries + [True, True, True]}, # Turn off connectors, keep points on
                connector_trace_indices + [num_countries, num_countries + 1, num_countries + 2] # Apply to all traces
            ],
            args2=[
                {'visible': [True] * num_countries + [True, True, True]}, # Turn on connectors, keep points on
                connector_trace_indices + [num_countries, num_countries + 1, num_countries + 2] # Apply to all traces
            ]
        )
    ],
    bgcolor='white',
    bordercolor='lightgrey',
    font=dict(size=14),
    pad=dict(r=10, t=10, b=10, l=10)
)
 
# Add the dropdown menu and the new toggle button to the layout
fig.update_layout(
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            x=0.84,           # Align right edge with annotation's right edge
            xanchor="left",  # Align right edge of dropdown with x
            y=0.18,           # Position slightly above the annotation
            yanchor="bottom",    # Align top of dropdown with y
            showactive=True,  # Keep this to show current selection
            buttons=buttons,
            bgcolor='white',
            bordercolor='lightgrey',
            font=dict(size=14),
            pad=dict(r=10, t=10, b=10, l=10) 
        ),
        toggle_connectors_button # Add the new button group
    ]
)

# Function to encode image to base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

LOGO_PATH = "logo_full_white_on_blue.jpg" # Update this path if necessary
if Path(LOGO_PATH).exists():
    encoded_image = get_image_as_base64(LOGO_PATH)
    fig.add_layout_image(
        dict(
            source=f"data:image/jpeg;base64,{encoded_image}",
            xref="paper", yref="paper",
            x=0.85, y=0.05,
            sizex=0.1, sizey=0.1, # Adjust size as needed
            xanchor="left", yanchor="bottom",
            layer="above"
        )
    )
else:
    print(f"Warning: Logo file not found at {LOGO_PATH}. Skipping logo display.")

fig.show()