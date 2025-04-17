# Proxmox VNC API with Nginx Proxy

This project provides a web-based interface to access Proxmox VMs and LXC containers via VNC. The backend is built using Flask, and Nginx is used as a reverse proxy to handle SSL termination and route requests to the Flask app and Proxmox API.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
   - [Step 1: Install Nginx](#step-1-install-nginx)
   - [Step 2: Configure Nginx](#step-2-configure-nginx)
   - [Step 3: Install Dependencies](#step-3-install-dependencies)
   - [Step 4: Run the Flask App](#step-4-run-the-flask-app)
3. [Accessing Proxmox VMs](#accessing-proxmox-vms)
4. [Troubleshooting](#troubleshooting)
5. [Contributing](#contributing)
6. [License](#license)

---

## Prerequisites

Before proceeding, ensure you have the following:

- A server or machine with Ubuntu/Debian (or any Linux distribution that supports Nginx).
- Python 3.8+ installed.
- Access to a Proxmox server with the API enabled.
- Root or sudo privileges on the server.

---

## Installation Steps

### Step 1: Install Nginx

1. Update your package list:
   ```bash
   sudo apt update
   ```

2. Install Nginx:
   ```bash
   sudo apt install nginx -y
   ```

3. Start and enable Nginx to run on boot:
   ```bash
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

4. Verify that Nginx is running:
   ```bash
   sudo systemctl status nginx
   ```

   You should see output indicating that Nginx is active and running.

---

### Step 2: Configure Nginx

1. Replace `[ENTER_YOUR_IP_HERE]` in the Nginx configuration file with your actual IP address or domain name. For example:
   ```plaintext
   server_name [ENTER_YOUR_IP_HERE];
   ```
   becomes:
   ```plaintext
   server_name 192.168.1.122;
   ```

2. Copy the updated Nginx configuration file to `/etc/nginx/sites-available/`:
   ```bash
   sudo cp nginx-config-file.conf /etc/nginx/sites-available/proxmox-vnc
   ```

   Replace `nginx-config-file.conf` with the name of your Nginx configuration file.

3. Create a symbolic link to enable the configuration:
   ```bash
   sudo ln -s /etc/nginx/sites-available/proxmox-vnc /etc/nginx/sites-enabled/
   ```

4. Test the Nginx configuration for syntax errors:
   ```bash
   sudo nginx -t
   ```

   If no errors are found, restart Nginx to apply the changes:
   ```bash
   sudo systemctl restart nginx
   ```

---

### Step 3: Install Dependencies

1. Install Python dependencies:
   ```bash
   pip install flask python-dotenv requests
   ```

2. Create a `.env` file in the root directory of your project and add your Proxmox credentials:
   ```plaintext
   PROXMOX_USERNAME=your proxmox username
   PROXMOX_PASSWORD=proxmox password
   PROXMOX_HOST=proxmox ip 
   PROXMOX_NODES=proxmox nodes seperated by commas
   PROXMOX_PORT=proxmox port 
   ```

   Replace the values with your actual Proxmox server details.

---

### Step 4: Run the Flask App

1. Start the Flask application:
   ```bash
   python app.py
   ```

   By default, the app will run on `http://0.0.0.0:5000`.

2. Open your browser and navigate to `https://[YOUR_IP]/don` to access the frontend.

---

## Accessing Proxmox VMs

1. **Enter the VM ID**:
   - On the frontend page (`https://[YOUR_IP]/don`), enter the ID of the VM or LXC container you want to access.

2. **Open the VNC Console**:
   - Click the "Open VNC Console" button. The app will authenticate with the Proxmox API, generate a VNC URL, and open the console in a new tab.

3. **Interact with the VM**:
   - Use the VNC console to interact with your Proxmox VM or LXC container as if you were accessing it directly.

---

## Troubleshooting

### Common Issues and Solutions

1. **Nginx Fails to Start**:
   - Check the Nginx error logs for details:
     ```bash
     sudo journalctl -u nginx
     ```
   - Ensure there are no syntax errors in your configuration file by running:
     ```bash
     sudo nginx -t
     ```

2. **Proxmox API Authentication Fails**:
   - Verify that the credentials in the `.env` file are correct.
   - Ensure the Proxmox API is accessible from your server.

3. **SSL Certificate Errors**:
   - If you’re using self-signed certificates, browsers may show a warning. For production, consider using a trusted certificate from Let’s Encrypt.

4. **VNC Console Not Loading**:
   - Ensure WebSocket connections are properly configured in the Nginx configuration.
   - Check the browser console for errors related to cookies or WebSocket connections.

---

## Contributing

Contributions are welcome! If you'd like to contribute, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature or fix"
   ```
4. Push your branch to GitHub:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---
