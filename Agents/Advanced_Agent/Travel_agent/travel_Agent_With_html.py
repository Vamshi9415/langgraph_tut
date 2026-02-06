from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient

def build_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "travel_server": {
                "transport": "streamable_http",
                "url": "https://mcp.kiwi.com"
            }
        }
    )

async def fetch_mcp_context(client: MultiServerMCPClient):
    print("Getting Tools")
    tools = await client.get_tools()
    print("Tools retrieved")
    return tools

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

def build_agent(tools):
    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="You are a travel agent. Today is Friday, Feb 6, 2026. Use the tools to get the perfect plan."
    )
    return agent

def config():
    return {
        "configurable": {
            "thread_id": "1"
        }
    }

from langchain.messages import HumanMessage

async def run_Agent(agent, config):
    query = HumanMessage(content="Get me a direct flight from Hyderabad to Chennai on March 31st")
    response = await agent.ainvoke(
        {
            'messages': [query],
        }, config
    )
    return response

def format_duration(seconds):
    """Convert seconds to human readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def parse_flight_data(response):
    """Extract flight data from the response messages"""
    flights = []
    
    for msg in response['messages']:
        if hasattr(msg, 'content') and isinstance(msg.content, list):
            for content_item in msg.content:
                if isinstance(content_item, dict) and content_item.get('type') == 'text':
                    try:
                        # Try to parse JSON from the text content
                        flight_data = json.loads(content_item['text'])
                        if isinstance(flight_data, list):
                            flights = flight_data
                            break
                    except:
                        pass
    
    return flights

def generate_html_report(response):
    """Generate comprehensive HTML file from the agent response"""
    
    # Parse flight data
    flights = parse_flight_data(response)
    
    if not flights:
        return None
    
    # Separate direct and connecting flights
    direct_flights = [f for f in flights if 'layovers' not in f or not f['layovers']]
    connecting_flights = [f for f in flights if 'layovers' in f and f['layovers']]
    
    # Sort by price
    direct_flights.sort(key=lambda x: x['price'])
    
    def create_flight_table(flights_list, table_title):
        if not flights_list:
            return ""
        
        rows = ""
        for flight in flights_list:
            departure_time = flight['departure']['local'].split('T')[1][:5]
            arrival_time = flight['arrival']['local'].split('T')[1][:5]
            departure_date = flight['departure']['local'].split('T')[0]
            duration = format_duration(flight['durationInSeconds'])
            
            # Handle layovers
            route = f"{flight['flyFrom']} → {flight['flyTo']}"
            if 'layovers' in flight and flight['layovers']:
                layover_codes = [layover['at'] for layover in flight['layovers']]
                route = f"{flight['flyFrom']} → {' → '.join(layover_codes)} → {flight['flyTo']}"
            
            rows += f"""
                <tr>
                    <td><strong>{route}</strong><br><small>{flight['cityFrom']} to {flight['cityTo']}</small></td>
                    <td>{departure_date}<br>{departure_time} → {arrival_time}</td>
                    <td class="duration">{duration}</td>
                    <td class="price">{flight['price']} {flight['currency']}</td>
                    <td><a href="{flight['deepLink']}" target="_blank">Book Now</a></td>
                </tr>
            """
        
        return f"""
            <h3>{table_title}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Date & Time</th>
                        <th>Duration</th>
                        <th>Price</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        """
    
    # Generate tables
    direct_table = create_flight_table(direct_flights, "✈️ Direct Flights")
    connecting_table = create_flight_table(connecting_flights, "🔄 Connecting Flights")
    
    # Calculate statistics
    if direct_flights:
        cheapest_price = min(f['price'] for f in direct_flights)
        shortest_duration = min(f['durationInSeconds'] for f in direct_flights)
        avg_price = sum(f['price'] for f in direct_flights) / len(direct_flights)
    else:
        cheapest_price = 0
        shortest_duration = 0
        avg_price = 0
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Search Results - Hyderabad to Chennai</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.95;
            margin: 5px 0;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9ff;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        
        .stat-card h4 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-card p {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        h3 {{
            color: #667eea;
            margin: 40px 0 20px 0;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0 40px 0;
            background: white;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        th {{
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 18px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9ff;
            transform: scale(1.01);
            transition: all 0.2s ease;
        }}
        
        tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        a {{
            color: white;
            background: #667eea;
            text-decoration: none;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 5px;
            transition: all 0.3s ease;
            display: inline-block;
        }}
        
        a:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .price {{
            font-weight: bold;
            color: #27ae60;
            font-size: 1.2em;
        }}
        
        .duration {{
            color: #e74c3c;
            font-weight: 600;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 25px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        small {{
            color: #888;
            font-size: 0.85em;
        }}
        
        .no-flights {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✈️ Flight Search Results</h1>
            <p><strong>Hyderabad (HYD)</strong> → <strong>Chennai (MAA)</strong></p>
            <p>📅 March 31, 2026</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h4>Total Flights Found</h4>
                <p>{len(flights)}</p>
            </div>
            <div class="stat-card">
                <h4>Cheapest Price</h4>
                <p>{cheapest_price} EUR</p>
            </div>
            <div class="stat-card">
                <h4>Shortest Duration</h4>
                <p>{format_duration(shortest_duration)}</p>
            </div>
            <div class="stat-card">
                <h4>Direct Flights</h4>
                <p>{len(direct_flights)}</p>
            </div>
        </div>
        
        <div class="content">
            {direct_table}
            {connecting_table if connecting_flights else ''}
            
            <div style="background: #fff4e6; border-left: 5px solid #ff9800; padding: 20px; margin: 30px 0; border-radius: 5px;">
                <h4 style="color: #ff9800; margin-bottom: 10px;">💡 Travel Tip</h4>
                <p><strong>Did you know?</strong> Chennai is often referred to as the "Detroit of India" due to its significant automobile industry. It's also home to Marina Beach, one of the longest urban beaches in the world!</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</strong></p>
            <p>Powered by Kiwi.com Flight Search API | Data subject to availability and change</p>
            <p style="margin-top: 10px; color: #999; font-size: 0.85em;">All prices shown are in EUR. Please check the booking site for final prices and availability.</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save to file - use current directory for cross-platform compatibility
    import os
    output_path = os.path.join(os.getcwd(), 'flight_results.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"\n✅ HTML report generated: {output_path}")
    print(f"📊 Found {len(flights)} flights ({len(direct_flights)} direct, {len(connecting_flights)} connecting)")
    return output_path

async def main():
    client = build_client()
    tools = await fetch_mcp_context(client=client)
    agent = build_agent(tools)
    my_config = config()
    response = await run_Agent(agent, my_config)
    
    # Generate HTML report
    html_path = generate_html_report(response)
    
    if html_path:
        print("\n" + "="*60)
        print("  Flight search complete!")
        print(f" Results saved to: {html_path}")
        print("="*60)
    else:
        print("  No flight data found to generate report")

import asyncio
if __name__ == "__main__":
    asyncio.run(main())