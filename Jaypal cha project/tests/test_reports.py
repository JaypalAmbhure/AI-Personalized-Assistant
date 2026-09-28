from datetime import date
from app.models import Category

def test_reports_page_and_csv_export(auth_client, app):
    # Add a sample expense
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    auth_client.post('/expenses/add', data={
        'amount': '150.00',
        'category_id': str(cat_id),
        'description': 'Target Household Items',
        'date': date.today().strftime('%Y-%m-%d'),
        'payment_method': 'Credit Card',
        'is_need': 'true'
    }, follow_redirects=True)

    # 1. Access reports page
    res = auth_client.get('/reports', follow_redirects=True)
    assert res.status_code == 200
    assert b'Financial Performance Statement' in res.data

    # 2. Access CSV export
    csv_res = auth_client.get('/reports/export/csv')
    assert csv_res.status_code == 200
    assert 'text/csv' in csv_res.headers['Content-Type']
    assert b'Target Household Items' in csv_res.data or b'Type,Date,Category' in csv_res.data
