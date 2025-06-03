# graph.py
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for rendering plots as PNG
import matplotlib.pyplot as plt

def graph(times, pressures):
    cleaned_data = [(t, p) for t, p in zip(times, pressures) if t is not None and p is not None]
    if not cleaned_data:
        raise ValueError("No valid data to plot.")

    clean_times, clean_pressures = zip(*cleaned_data)

    fig, ax = plt.subplots(figsize=(6, 6))

    # Line and scatter plot with markers
    ax.plot(clean_times, clean_pressures, linestyle='-', marker='o', color='blue', label="Pressure vs Time")
    ax.scatter(clean_times, clean_pressures, color='red', zorder=5)

    # Annotate each point
    for t, p in zip(clean_times, clean_pressures):
        offset_y = 10 # Increase default offset
        if p == 0: # If pressure is 0, nudge the label up more significantly to avoid overlap with x-axis
            offset_y = 15

        ax.annotate(
            f"{p:.0f} PSI",
            xy=(t, p),
            xytext=(10, offset_y), # Increased offset from the point
            textcoords='offset points',
            fontsize=11,           # Increased font size for better readability
            color='darkgreen',
            fontweight='bold',     # Make text bold
            bbox=dict(             # Add a bounding box
                boxstyle="round,pad=0.3", # Rounded box with some padding
                fc="yellow",              # Fill color of the box (e.g., yellow for contrast)
                ec="darkgreen",           # Edge color of the box
                lw=0.5,                   # Line width of the box edge
                alpha=0.7                 # Transparency of the box (0.7 means 70% opaque)
            )
        )


    # --- Altered Axis Limits Section ---
    # Determine the min and max for x and y axes
    min_time = min(clean_times)
    max_time = max(clean_times)
    min_pressure = min(clean_pressures)
    max_pressure = max(clean_pressures)

    # Set x-axis limits: start from 0 or slightly before the min_time, end slightly after max_time
    # Ensure x-axis starts at 0 if the data starts at 0 or very close to it
    x_lower_limit = 0 if min_time >= 0 else min_time - (max_time - min_time) * 0.05
    x_upper_limit = max_time + (max_time - min_time) * 0.05
    if x_upper_limit < 40: # Ensure x-axis extends at least to 40 if needed
        x_upper_limit = 40
    ax.set_xlim(x_lower_limit, x_upper_limit)

    # Set y-axis limits: always include 0, and add padding at the top
    y_lower_limit = 0 if min_pressure >= 0 else min_pressure - (max_pressure - min_pressure) * 0.05
    y_upper_limit = max_pressure + (max_pressure - min_pressure) * 0.10 # 10% padding at the top
    ax.set_ylim(y_lower_limit, y_upper_limit)
    # --- End Altered Axis Limits Section ---

    # Axis labels and styling
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Pressure (PSI)")
    ax.set_title("Pressure Over Time")
    ax.grid(True)
    ax.legend()

    # Click event handler
    def onclick(event):
        if event.inaxes == ax:
            x_coord = int(event.xdata)
            y_coord = int(event.ydata)
            print(f"Clicked on grid: ({x_coord}, {y_coord})")

    fig.canvas.mpl_connect('button_press_event', onclick)

    return fig,ax
