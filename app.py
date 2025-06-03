# app.py

from flask import Flask, request, jsonify, render_template
from calculator import calculate_minimum_gas, calculate_turn_data
from graph import graph # Assuming 'graph' is a function that returns a matplotlib figure and axes
import matplotlib.pyplot as plt
import io
import base64

# --- ONLY ONE FLASK APP INSTANCE ---
app = Flask(__name__)

# Helper function to convert matplotlib figure to base64 image
def fig_to_base64(fig):
    """
    Converts a matplotlib figure to a base64 encoded PNG image.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig) # Close the figure to free up memory
    return img_base64

# --- Define Routes ---

@app.route('/')
def index():
    """
    Renders the main HTML page for the dive gas planner.
    """
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Handles POST requests for dive gas calculations.
    Receives SAC, depth, tank, config, and start_pressure.
    Returns calculated dive data and a graph image.
    """
    data = request.get_json()
    try:
        sac = float(data['sac'])
        depth = float(data['depth'])
        tank = data['tank']
        config = data['config']
        start_pressure = float(data['start_pressure'])

        # Calculate minimum gas
        minimum_gas, _ = calculate_minimum_gas(sac, depth, tank, config)

        # Calculate turnaround info
        turn_data = calculate_turn_data(start_pressure, minimum_gas, tank, config, sac, depth)

        # Prepare data for graph and round values for display
        time_descend = round(turn_data['time_descending'], 0)
        time_before_turn = round(turn_data['time_before_turn'], 0)
        total_duration = round(turn_data['total_dive_time_min'])
        time_ascend = round(turn_data['time_ascending'])
        rounded_minimum_gas = round(minimum_gas) # Use a rounded value for display

        # Data points for the graph
        times = [0, time_descend, time_before_turn, (time_ascend + time_before_turn), total_duration]
        pressures = [start_pressure, None, turn_data['turn_pressure'], None, rounded_minimum_gas] # Use turn_data['turn_pressure'] directly

        # Generate graph
        fig, ax = graph(times, pressures)
        img_base64 = fig_to_base64(fig) # fig_to_base64 now closes the figure

        return jsonify({
            'minimum_gas': rounded_minimum_gas,
            'turn_pressure': round(turn_data['turn_pressure']),
            'gas_before_turn_psi': round(turn_data['gas_before_turn_psi'], 2), # Keep some precision for PSI
            'gas_before_turn_cf': round(turn_data['gas_before_turn_cf'], 0),
            'total_dive_time_min': round(turn_data['total_dive_time_min'], 2), # Keep some precision for total time
            'time_before_turn': round(turn_data['time_before_turn'], 0),
            'usable_gas': round(turn_data['usable_gas'], 0),
            'graph_img': img_base64
        })
    except Exception as e:
        # Return specific error message from calculator functions
        return jsonify({'error': str(e)}), 400

# --- Entry point for local development ---
# This block is not executed when deployed with a WSGI server like Gunicorn.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) # Listen on all interfaces and specified port