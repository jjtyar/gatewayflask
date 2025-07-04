from flask import Flask, request, jsonify
import joblib
import json
from azure.iot.device import IoTHubDeviceClient, Message
import os

app = Flask(__name__)

# Debug: Get working directory and expected model path
working_dir = os.getcwd()
model_path = os.path.join(os.path.dirname(__file__), 'decision_tree_model.joblib')

print("Current working directory:", working_dir)
print("Expected model path:", model_path)

try:
    model = joblib.load(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Failed to load model: {e}")
    model = None
    model_load_error = str(e)  # Save the error to return in the response

# IoT Hub Connection String (hardcoded as you requested)
IOTHUB_DEVICE_CONNECTION_STRING = 'HostName=homesafetyhub.azure-devices.net;DeviceId=gatewaydevice;SharedAccessKey=8HLMsfUW4hRaJuoIq3HvNTj4USn2rqvof8jF9qaLkBs='

def create_iot_client():
    try:
        client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_DEVICE_CONNECTION_STRING)
        return client
    except Exception as e:
        print(f"Failed to create IoT Hub client: {e}")
        return None

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

        if model is None:
            return jsonify({
                'status': 'Error',
                'message': 'Model not loaded',
                'working_directory': working_dir,
                'expected_model_path': model_path,
                'model_load_error': model_load_error
            }), 500

        prediction = model.predict([features])[0]
        data['anomaly_flag'] = bool(prediction)

        device_client = create_iot_client()
        if device_client:
            iot_message = Message(json.dumps(data))
            device_client.send_message(iot_message)
        else:
            print("IoT client unavailable, skipping sending message.")

        return jsonify({'status': 'Processed and sent to IoT Hub', 'processed_data': data}), 200

    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
