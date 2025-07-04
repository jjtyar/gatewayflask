from flask import Flask, request, jsonify
import joblib
import json
from azure.iot.device import IoTHubDeviceClient, Message

app = Flask(__name__)


# Load the model
model = joblib.load('decision_tree_model.joblib')

# IoT Hub Connection String (replace with your actual value)
IOTHUB_DEVICE_CONNECTION_STRING = '<Your IoT Hub Device Connection String>'

# Create IoT Hub Client
device_client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_DEVICE_CONNECTION_STRING)

@app.route('/gateway', methods=['POST'])
def gateway():
    try:
        data = request.get_json()

        features = [
            data.get('sensor_temp', 0),
            data.get('sensor_gas', 0),
            data.get('sensor_co', 0),
            data.get('sensor_sound', 0),
            data.get('sensor_smoke', 0)
        ]

        prediction = model.predict([features])[0]
        data['anomaly_flag'] = bool(prediction)

        # Send to IoT Hub
        iot_message = Message(json.dumps(data))
        device_client.send_message(iot_message)

        return jsonify({'status': 'Processed and sent to IoT Hub', 'processed_data': data}), 200

    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
