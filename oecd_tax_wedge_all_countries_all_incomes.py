import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Plot tax wedge curves for all OECD countries across different
# household scenarios. The input data comes from the OECD's
# tax wedge spreadsheet.

# Path to the downloaded OECD spreadsheet
file_path = '/Users/dan/Dan/tax policy associates/OECD tax wedges all countries all incomes 2024.xlsx'
# Add a little padding to the x-axis so the final labels have room
X_SPACING = 0.1

# -----------------------------------------------------------------
# 1. Load all four scenarios from the spreadsheet
# Each sheet represents a different household type
# -----------------------------------------------------------------
sheet_names = [
    "single_no_children",
    "single_two_children",
    "married_2_children",
    "married_no_children"
]

dfs = {}
for sheet in sheet_names:
    tmp = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=8,
        usecols='B:AO',
        index_col=0
    )
    # Clean up the index values and turn them into numbers
    tmp.index = (
        tmp.index
           .str.replace('% of average wage', '', regex=False)
           .astype(float)
    )
    # Interpolate missing values so the lines are smooth
    dfs[sheet] = tmp.interpolate(method='linear', axis=0)

# Determine common x-axis limits across all scenarios
min_x = min(d.index.min() for d in dfs.values())
max_x = max(d.index.max() for d in dfs.values())
# Add some extra space so country names don't get clipped
extended_max_x = max_x * (1 + X_SPACING)


# -----------------------------------------------------------------
# 3. Prepare colours and layout for the logo
# -----------------------------------------------------------------
colours = [
    "black", "blue", "blueviolet", "brown", "cadetblue", "chocolate", "coral", "crimson", "cyan", "darkblue",
    "darkcyan", "darkgoldenrod", "darkgreen", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkslateblue",
    "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dodgerblue", "firebrick", "forestgreen", "fuchsia", "green",
    "hotpink", "indianred", "indigo", "maroon", "mediumblue", "mediumorchid", "mediumseagreen", "mediumslateblue", "orangered", "purple"
]
red_country = "United Kingdom"

# Load and position the Tax Policy Associates logo
logo = Image.open("logo_full_white_on_blue.jpg")
logo_layout = [dict(
    source=logo, xref="paper", yref="paper",
    x=1.1, y=1.02, sizex=0.1, sizey=0.1,
    xanchor="right", yanchor="bottom"
)]

# -----------------------------------------------------------------
# 4. Build the figure
# -----------------------------------------------------------------


fig = go.Figure()
# Countries to highlight when the chart first loads
highlight = ['United Kingdom', 'United States', 'France', 'Germany', 'Italy', 'Spain', 'Canada', 'Sweden', 'Belgium', 'Netherlands', 'Poland', 'Türkiye']

default_sheet = sheet_names[0]   # "single_no_children"
# Create one trace per country for each scenario
for sheet in sheet_names:
    df_sheet = dfs[sheet]
    for idx, country in enumerate(df_sheet.columns):
        # Determine initial visibility for this sheet/country
        if sheet == default_sheet:
            vis = True if country in highlight else 'legendonly'
        else:
            vis = False

        # Only show the country name on the last point of the line
        txt = [''] * (len(df_sheet.index) - 1) + [country]

        fig.add_trace(go.Scatter(
            x=df_sheet.index,
            y=df_sheet[country],
            mode='lines+text',
            line_shape='spline',
            name=country,
            legendgroup=country,
            visible=vis,
            line=dict(width=2, color='red' if country == red_country else colours[idx]),
            opacity=0.8,
            text=txt,
            textposition='middle right',
            textfont=dict(
                size=12,
                color='red' if country == red_country else colours[idx]
            ),
            hovertemplate=f"{country} %{{y:.1f}}%<extra></extra>",
        ))

# -----------------------------------------------------------------
# 5. Dropdown to toggle between household scenarios
# -----------------------------------------------------------------
buttons = []
for sheet in sheet_names:
    label = sheet.replace('_', ' ').title()
    mask = []
    for s in sheet_names:
        for country in dfs[s].columns:
            if s == sheet:
                # default‐sheet countries: highlighted ones on, others legendonly
                mask.append(True if country in highlight else 'legendonly')
            else:
                # all other sheets start fully hidden
                mask.append(False)
    # Store the button configuration for this scenario
    buttons.append(dict(
        label=label,
        method='update',
        args=[{'visible': mask}]
    ))

fig.update_layout(
    # Add the dropdown menu to the figure
    updatemenus=[dict(
        buttons=buttons,
        direction='down',
        x=0.5,
        xanchor='center',
        y=1.0,
        yanchor='bottom'
    )]
)

# -----------------------------------------------------------------
# 6. Update layout with bigger fonts and the logo
# -----------------------------------------------------------------
fig.update_layout(
    # Chart title and axis styling
    title=dict(text='OECD tax wedge by income level for each country (2024)', font=dict(size=32), x=0.5, xanchor='center'),
    xaxis=dict(
        title='Income level (% of average wage)',
        title_font=dict(size=24),
        tickfont=dict(size=14),
        range=[min_x, extended_max_x],
        ticksuffix='%',
    ),
    yaxis=dict(
        title='Tax wedge (%)',
        title_font=dict(size=24),  
        tickfont=dict(size=14),
        ticksuffix='%',     
    ),
    template='plotly_white',
    hovermode='x unified',
    images=logo_layout
)

# -----------------------------------------------------------------
# 7. Show the plot or export to HTML
# -----------------------------------------------------------------
fig.show()
fig.write_html('oecd_tax_wedge_incomes_and_countries.html', include_plotlyjs='cdn')
