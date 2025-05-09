# DebtSweeper Deployment Guide for SiteGround

This guide will help you deploy the DebtSweeper application on SiteGround hosting.

## Step 1: Access SiteGround Control Panel

1. Log in to your SiteGround account
2. Go to the "Site Tools" for your debtsweeper.dev domain

## Step 2: Set Up Domain

1. Go to "Domain" > "Manage"
2. Ensure debtsweeper.dev is properly set up
3. If not already configured, go to "DNS Settings" and set the DNS records according to SiteGround's instructions

## Step 3: Set Up SSH Access

1. In Site Tools, go to "Dev" > "SSH Keys Manager"
2. Generate a new SSH key or add an existing one
3. Once SSH is set up, connect to your server using the command provided by SiteGround

## Step 4: Upload Application Files

**Option 1: Using Site Tools File Manager**

1. Go to "Site" > "File Manager"
2. Create a new directory called "debtsweeper" in your public_html folder
3. Upload all the application files to this directory

**Option 2: Using SFTP**

1. Use an SFTP client like FileZilla
2. Connect to your SiteGround server using your SSH credentials
3. Create a new directory called "debtsweeper" in your public_html folder
4. Upload all the application files to this directory

## Step 5: Set Up Python Environment

Connect to your server via SSH and run the following commands:

```bash
cd ~/public_html/debtsweeper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 6: Set Up Application Entry Point

For a guaranteed working debt knowledge graph visualization, use the `simple_graph_app.py` file as your main application:

1. **Edit passenger_wsgi.py** to use `simple_graph_app.py`:

```python
import sys, os
INTERP = os.path.join(os.getcwd(), 'venv', 'bin', 'python3')
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.getcwd())

# Import from simple_graph_app.py
from simple_graph_app import app as application
```

2. Verify these configuration files are in your debtsweeper directory:
   - **passenger_wsgi.py** - Entry point for the application (updated as above)
   - **simple_graph_app.py** - Contains the simplified graph visualization
   - **.htaccess** - Apache configuration
   - **requirements.txt** - Python dependencies (ensure it includes networkx==3.1)

**Important Notes:**
- The `simple_graph_app.py` file provides a simplified but guaranteed-to-work graph visualization
- It includes extensive debug logging visible in the browser 
- If you prefer the full application features, you can use `graph_app.py` instead, but `simple_graph_app.py` offers the most reliable graph rendering

## Step 7: Set Up SSL Certificate

1. In Site Tools, go to "Security" > "SSL Manager"
2. Issue a Let's Encrypt SSL certificate for debtsweeper.dev
3. Enable HTTPS Enforce if you want all traffic to be secure

## Step 8: Restart Application (if needed)

If changes don't take effect immediately, you may need to restart the application:

```bash
cd ~/public_html/debtsweeper
touch tmp/restart.txt
```

## Troubleshooting

If you encounter issues:

1. Check the error logs in Site Tools > "Statistics" > "Error Logs"
2. Verify permissions on your files (files should be 644, directories 755)
3. Make sure the paths in passenger_wsgi.py match your actual environment

### Graph Visualization Troubleshooting

If the debt knowledge graph isn't displaying properly:

1. **Use simplified app**: Switch to using `simple_graph_app.py` via passenger_wsgi.py for guaranteed graph rendering
2. **Check debug log**: The simplified app includes an on-screen debug log showing initialization state
3. **Check browser console**: The graph visualization includes extensive console logging for debugging
4. **Verify Cytoscape.js**: Make sure it's loaded properly (check network tab in browser dev tools)
5. **Container size**: Ensure the graph container has proper dimensions (at least 600px height)
6. **Data format**: Check that the graph data JSON format is correct with nodes and edges arrays
7. **Network issues**: If using a slow connection, the graph may take longer to initialize (up to 2-3 seconds)

For additional support, contact SiteGround customer service or refer to their Python application hosting documentation.