from flask import Flask, request, jsonify, send_from_directory, make_response
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load Proxmox credentials and configuration from environment variables
USERNAME = os.getenv("PROXMOX_USERNAME")
PASSWORD = os.getenv("PROXMOX_PASSWORD")
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
NODES = os.getenv("PROXMOX_NODES", "").split(",")  # Convert comma-separated string to list
PORT = int(os.getenv("PROXMOX_PORT", 8006))  # Default port is 8006 if not specified

@app.route('/')
def index():
    print("Debug: Serving index.html")  # Debugging statement
    return send_from_directory('.', 'index.html')

@app.route('/don')
def don():
    print("Debug: Serving index.html for /don")  # Debugging statement
    return send_from_directory('.', 'index.html')

@app.route('/api/open-vnc', methods=['GET'])
def open_vnc():
    vmid = request.args.get('vmid')
    print(f"Debug: Received request with ID={vmid}")  # Debugging statement

    if not vmid or not vmid.isdigit():
        print("Debug: Invalid ID provided.")  # Debugging statement
        return jsonify({"error": "Invalid ID"}), 400

    # Step 1: Authenticate with Proxmox API
    try:
        auth_url = f"https://{PROXMOX_HOST}:{PORT}/api2/json/access/ticket"
        auth_data = {"username": USERNAME, "password": PASSWORD}
        auth_response = requests.post(auth_url, data=auth_data, verify=False)
        if auth_response.status_code != 200:
            print(f"Debug: Authentication failed: {auth_response.text}")
            return jsonify({"error": "Authentication failed"}), 500
        auth_data = auth_response.json().get("data", {})
        pve_auth_cookie = auth_data.get("ticket")
        csrf_token = auth_data.get("CSRFPreventionToken")
        if not pve_auth_cookie or not csrf_token:
            print("Debug: Missing PVEAuthCookie or CSRFPreventionToken.")
            return jsonify({"error": "Authentication failed"}), 500
        print(f"Debug: Authentication successful. PVEAuthCookie={pve_auth_cookie}, CSRFPreventionToken={csrf_token}")
    except Exception as e:
        print(f"Debug: Error during authentication: {e}")
        return jsonify({"error": str(e)}), 500

    # Step 2: Search for VM or LXC container across all nodes
    resource_type = None
    vnc_url = None
    selected_node = None

    for node in NODES:
        try:
            # Check if the ID is a VM
            vm_url = f"https://{PROXMOX_HOST}:{PORT}/api2/json/nodes/{node}/qemu/{vmid}/config"
            vm_response = requests.get(vm_url, headers={
                "Cookie": f"PVEAuthCookie={pve_auth_cookie}",
                "CSRFPreventionToken": csrf_token
            }, verify=False)

            if vm_response.status_code == 200:
                vm_data = vm_response.json().get("data", {})
                if vm_data:
                    resource_type = "VM"
                    selected_node = node
                    print(f"Debug: ID={vmid} is a VM on node={selected_node}.")
                    vm_name = vm_data.get("name")
                    if not vm_name:
                        print("Debug: Failed to fetch VM name. Check if the VM exists.")
                        return jsonify({"error": "VM not found"}), 404
                    print(f"Debug: Fetched VM name: VMNAME={vm_name}")
                    vnc_url = f"https://192.168.1.122/?console=kvm&novnc=1&vmid={vmid}&vmname={vm_name}&node={selected_node}&resize=off&cmd="
                    print(f"Debug: Constructed VNC URL: {vnc_url}")
                    break  # Exit loop once VM is found
            else:
                print(f"Debug: VM ID={vmid} not found on node={node}. Status code: {vm_response.status_code}")

            # Check if the ID is an LXC container
            lxc_url = f"https://{PROXMOX_HOST}:{PORT}/api2/json/nodes/{node}/lxc/{vmid}/config"
            lxc_response = requests.get(lxc_url, headers={
                "Cookie": f"PVEAuthCookie={pve_auth_cookie}",
                "CSRFPreventionToken": csrf_token
            }, verify=False)

            if lxc_response.status_code == 200:
                lxc_data = lxc_response.json().get("data", {})
                if lxc_data:
                    resource_type = "LXC"
                    selected_node = node
                    print(f"Debug: ID={vmid} is an LXC container on node={selected_node}.")
                    container_name = lxc_data.get("hostname")
                    if not container_name:
                        print("Debug: Failed to fetch LXC container name. Check if the container exists.")
                        return jsonify({"error": "LXC container not found"}), 404
                    print(f"Debug: Fetched LXC container name: CONTAINER_NAME={container_name}")
                    vnc_url = f"https://[your-iphere]/?console=lxc&xtermjs=1&vmid={vmid}&vmname={container_name}&node={selected_node}&cmd="
                    print(f"Debug: Constructed VNC URL: {vnc_url}")
                    break  # Exit loop once LXC is found
            else:
                print(f"Debug: LXC ID={vmid} not found on node={node}. Status code: {lxc_response.status_code}")

        except Exception as e:
            print(f"Debug: Error fetching details for node={node}: {e}")
            continue  # Try the next node

    if not resource_type:
        print("Debug: Resource not found on any node.")
        return jsonify({"error": "Resource not found"}), 404

    # Step 3: Return the response to the frontend
    response = make_response(jsonify({
        "cookie": pve_auth_cookie,
        "host": "192.168.1.122",
        "vncUrl": vnc_url
    }))
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

if __name__ == '__main__':
    print("Debug: Starting Flask app...")  # Debugging statement
    app.run(host='0.0.0.0', port=5000, debug=True)  # Bind to 0.0.0.0 for external access
