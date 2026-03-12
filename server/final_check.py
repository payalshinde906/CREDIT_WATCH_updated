import asyncio
import asyncpg

async def check():
    try:
        conn = await asyncpg.connect('postgresql://postgres:2004@localhost:5432/creditdatawatch')
        
        print('--- All Companies ---')
        rows = await conn.fetch('SELECT id, company_name FROM companies')
        for r in rows:
            print(dict(r))
        
        print('\n--- company_credibility_index ---')
        rows = await conn.fetch('SELECT company_id, score, grade FROM company_credibility_index')
        for r in rows:
            print(dict(r))
        
        print('\n--- POs for Fresh Vendor Co & Sync Test Vendor ---')
        rows = await conn.fetch("SELECT id, vendor, status FROM purchase_orders WHERE vendor IN ('Fresh Vendor Co', 'Sync Test Vendor')")
        for r in rows:
            print(dict(r))
        
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    asyncio.run(check())
