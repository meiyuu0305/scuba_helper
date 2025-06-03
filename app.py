# app.py

from flask import Flask, request, jsonify, render_template
from calculator import calculate_minimum_gas, calculate_turn_data
from graph import graph
import matplotlib.pyplot as plt  # ✅ Needed for plt.close()
import io
import base64

app = Flask(__name__)

# ✅ Only keep one copy
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8') 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
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

        # Generate graph
        time_descend =round (turn_data['time_descending'],0)
        time_before_turn = round(turn_data['time_before_turn'],0)
        total_duration = round(turn_data['total_dive_time_min'])
        time_ascend = round(turn_data['time_ascending'])
        minimum_gas = round(minimum_gas)
        times = [0,time_descend, time_before_turn, (time_ascend+time_before_turn), total_duration]
        pressures = [start_pressure,None,turn_data['gas_before_turn_psi'], None ,minimum_gas]
        fig, ax = graph(times, pressures)
        img_base64 = fig_to_base64(fig)
        plt.close(fig) 
        return jsonify({
            'minimum_gas': round(minimum_gas),
            'turn_pressure': round(turn_data['turn_pressure']),
            'gas_before_turn_psi': turn_data['gas_before_turn_psi'],
            'gas_before_turn_cf': round(turn_data['gas_before_turn_cf'],0),
            'total_dive_time_min': turn_data['total_dive_time_min'], 
            'time_before_turn': turn_data['time_before_turn'],
            'usable_gas': round(turn_data['usable_gas'], 0),
            'graph_img': img_base64  
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
