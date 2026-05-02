import httpx
import asyncio

async def setup():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post('http://localhost:8000/sessions', json={
                'function_id': 'sphere_shifted', 
                'goal': 'min', 
                'max_steps': 1000000
            })
            if r.status_code == 200:
                print(f"Session created: {r.json()['session_code']}")
            else:
                print(f"Failed to create session: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(setup())
