from shiny.express import input, render, ui
from shared import pbp, batters
import numpy as np

ui.tags.style(':root { --bs-primary-rgb:58, 144, 152; }')

with ui.h2():
    "Batter Effectiveness vs. Strategic Fielder Positioning"

with ui.layout_columns(): 
    with ui.card():
        ui.card_header('wOBA', class_='bg-primary lead')
        @render.text
        def text0():
            try:
                df = pbp.loc[input.batter(), str(input.if_alignment()), str(input.of_alignment())]
                return str(round(df['wOBA'].mean(), 3))
            except:
                return
    with ui.card():
        ui.card_header('Change in wOBA From Standard Alignment', class_='bg-primary lead')
        @render.text
        def text1():
            try:
                st =  pbp.loc[input.batter(), 'st', 'st']
                df = pbp.loc[input.batter(), str(input.if_alignment()), str(input.of_alignment())]
                st_woba = st['wOBA'].mean()
                return str(round(df['wOBA'].mean() - st_woba, 3))
            except:
                return
    with ui.card():
        ui.card_header('At Bats', class_='bg-primary lead')
        @render.text
        def text2():
            try:
                df = pbp.loc[input.batter(), str(input.if_alignment()), str(input.of_alignment())]
                return str(len(df))
            except:
                return


with ui.card():
    ui.card_header('Spray Chart', class_='bg-primary lead')
    @render.plot
    def plot():
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(projection='polar')
        ax.set_theta_zero_location('N')
        ax.set_thetamin(-45)
        ax.set_thetamax(45)
        ax.set_rlim(0, 450)
        ax.grid(visible=False)
        ax.set_xticklabels([])

        if_theta = [0.785398, 0, -0.785398, 0, 0.785398]
        if_r = [90, 120, 90, 0, 90]

        ax.fill_between(np.linspace(-0.785398, 0.785398, 100), 0, 450, color='#065700', alpha=1, zorder=0, label='_nolegend_')
        ax.fill_between(np.linspace(-0.785398, 0.785398, 100), 0, 160, color='#f5e09d', alpha=1, zorder=1, label='_nolegend_')
        ax.fill_between(np.linspace(-0.785398, 0.785398, 100), 0, 100, color='#065700', alpha=1, zorder=2, label='_nolegend_')
        ax.scatter([0], [60.5], c='#f5e09d', zorder=3, label='_nolegend_')
        ax.plot(if_theta, if_r, c='#f5e09d', linewidth=10, zorder=3, label='_nolegend_')

        try:
            df = pbp.loc[input.batter(), str(input.if_alignment()), str(input.of_alignment())]

            pos_r = (list(df.loc[:, 'fielder_3_r']) +
                list(df.loc[:, 'fielder_4_r']) +
                list(df.loc[:, 'fielder_5_r']) +
                list(df.loc[:, 'fielder_6_r']) +
                list(df.loc[:, 'fielder_7_r']) +
                list(df.loc[:, 'fielder_8_r']) +
                list(df.loc[:, 'fielder_9_r']))

            pos_a = (list(df.loc[:, 'fielder_3_a']) +
                list(df.loc[:, 'fielder_4_a']) +
                list(df.loc[:, 'fielder_5_a']) +
                list(df.loc[:, 'fielder_6_a']) +
                list(df.loc[:, 'fielder_7_a']) +
                list(df.loc[:, 'fielder_8_a']) +
                list(df.loc[:, 'fielder_9_a']))
            
            hit_x = df['hc_x'] - 115
            hit_y = df['hc_y'] - 200

            hit_a = np.arctan(hit_x / hit_y)
            hit_r = df['hit_distance_sc']

            ax.scatter(pos_a, pos_r, c='lightblue', alpha=.1, zorder=4)
            ax.scatter(hit_a, hit_r, c='#ff4726', s=4, zorder=5)

            ax.scatter(hit_a[hit_r < 160].mean(), hit_r[hit_r < 160].mean(), c='#44ff33', s=75, zorder=5)
            ax.scatter(hit_a[hit_r >= 160].mean(), hit_r[hit_r >= 160].mean(), c='#44ff33', s=75, zorder=5)

            ax.legend(['Fielders', 'Balls In Play', 'Average Hit\nLocation'], loc='lower left')
        except:
            pass
        return fig

with ui.sidebar(bg='#3a9098', fg='#ffffff'):
    ui.input_selectize(
        'batter', 'Select Batter',
        choices=batters
    ),
    ui.input_radio_buttons(
        'if_alignment', 'Infielder Alignment',
        choices={'st':'Standard', 'sh':'Shifted'}
    ),
    ui.input_radio_buttons(
        'of_alignment', 'Outfielder Alignment',
        choices={'st':'Standard', 'sh':'Shaded'}
    )