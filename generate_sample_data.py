import json
from sample_data import sample_trades

# Convert dataclasses to dictionaries for JSON serialization

def trade_to_dict(t):
    return {
        'trade_id': t.trade_id,
        'user_id': t.user_id,
        'symbol': t.symbol,
        'asset_type': t.asset_type.value,
        'created_at': t.created_at.isoformat(),
        'status': t.status,
        'legs': [
            {
                'action': leg.action.value,
                'datetime': leg.datetime.isoformat(),
                'quantity': leg.quantity,
                'price': leg.price,
                'fee': leg.fee,
            }
            for leg in t.legs
        ],
        'tags': t.tags,
    }

if __name__ == '__main__':
    data = [trade_to_dict(t) for t in sample_trades]
    with open('frontend/sample_trades.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('Wrote', len(data), 'trades to frontend/sample_trades.json')
