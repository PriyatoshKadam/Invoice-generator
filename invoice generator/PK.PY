from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch  
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from num2words import num2words
import datetime

def create_invoice(invoice_data):
    # Create a PDF document
    pdf = SimpleDocTemplate("invoice.pdf", pagesize=A4)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = styles['Title']
    heading_style = styles['Heading2']

    if invoice_data.get('vpc.jpg'):
        logo = Image(invoice_data['vpc.jpg'])
        logo.drawHeight = 1*inch
        logo.drawWidth = 2*inch
        elements.append(logo)

    # Title
    elements.append(Spacer(1, 0.2 * inch))
    title = Paragraph("Tax Invoice/Bill of Supply/Cash Memo", title_style)
    elements.append(title)
    subtitle = Paragraph("(Original for Recipient)", normal_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2 * inch))

    # Seller Details
    seller_details = invoice_data['seller_details']
    seller_info = f"""
    <b>Sold By:</b><br/>
    {seller_details['name']}<br/>
    {seller_details['address']}<br/>
    {seller_details['city']}, {seller_details['state']}, {seller_details['pincode']}<br/>
    PAN No.: {seller_details['pan']}<br/>
    GST Registration No.: {seller_details['gst']}
    """
    elements.append(Paragraph(seller_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Billing and Shipping Details
    billing_details = invoice_data['billing_details']
    shipping_details = invoice_data['shipping_details']
    billing_info = f"""
    <b>Billing Address:</b><br/>
    {billing_details['name']}<br/>
    {billing_details['address']}<br/>
    {billing_details['city']}, {billing_details['state']}, {billing_details['pincode']}<br/>
    State/UT Code: {billing_details['state_code']}
    """
    shipping_info = f"""
    <b>Shipping Address:</b><br/>
    {shipping_details['name']}<br/>
    {shipping_details['address']}<br/>
    {shipping_details['city']}, {shipping_details['state']}, {shipping_details['pincode']}<br/>
    State/UT Code: {shipping_details['state_code']}
    """
    elements.append(Paragraph(billing_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(shipping_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Order and Invoice Details
    order_details = invoice_data['order_details']
    invoice_details = invoice_data['invoice_details']
    order_info = f"""
    <b>Order Details:</b><br/>
    Order No.: {order_details['order_no']}<br/>
    Order Date: {order_details['order_date']}<br/>
    <b>Invoice Details:</b><br/>
    Invoice No.: {invoice_details['invoice_no']}<br/>
    Invoice Date: {invoice_details['invoice_date']}<br/>
    Reverse Charge: {invoice_details['reverse_charge']}
    """
    elements.append(Paragraph(order_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Place of Supply and Delivery
    place_of_supply = f"<b>Place of Supply:</b> {invoice_data['place_of_supply']}<br/>"
    place_of_delivery = f"<b>Place of Delivery:</b> {invoice_data['place_of_delivery']}<br/>"
    elements.append(Paragraph(place_of_supply, normal_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(place_of_delivery, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Item Details Table
    item_data = [['Sl. No', 'Description', 'Unit Price', 'Qty', 'Net Amount', 'Tax Rate', 'Tax Type', 'Tax Amount', 'Total Amount']]
    total_amount = 0

    for index, item in enumerate(invoice_data['items'], start=1):
        net_amount = item['unit_price'] * item['quantity']
        if invoice_data['place_of_supply'] == invoice_data['place_of_delivery']:
            tax_type = 'CGST/SGST'
            tax_rate = 2.5
            tax_amount = net_amount * (tax_rate / 100)
            tax_amount_total = tax_amount * 2
        else:
            tax_type = 'IGST'
            tax_rate = 5
            tax_amount_total = net_amount * (tax_rate / 100)
        total_amount += net_amount + tax_amount_total
        item_data.append([index, item['description'], f"{item['unit_price']:.2f}", item['quantity'],
                          f"{net_amount:.2f}", f"{tax_rate * 2 if tax_type == 'CGST/SGST' else tax_rate}%",
                          tax_type, f"{tax_amount_total:.2f}", f"{net_amount + tax_amount_total:.2f}"])

    table = Table(item_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Total Amount
    total_row = f"<b>Total Amount:</b> {total_amount:.2f}<br/><b>Amount in Words:</b> {num2words(total_amount, to='currency', lang='en_IN')}"
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(total_row, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Signature
    signature = f"""
    <b>For {invoice_data['seller_details']['name']}:</b><br/>
    <img src="{invoice_data['signature_image']}" width="100" height="50"/><br/>
    Authorised Signatory
    """
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(signature, normal_style))

    # Build PDF
    pdf.build(elements)

# Example invoice data
invoice_data = {
    'logo': '/mnt/data/1693544889.webp',  # Using the uploaded file for the logo
    'seller_details': {
        'name': 'Varasiddhi Silk Exports',
        'address': '75, 3rd Cross, Lalbagh Road',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560027',
        'pan': 'AACFV3325K',
        'gst': '29AACFV3325K1ZY'
    },
    'place_of_supply': 'Karnataka',
    'billing_details': {
        'name': 'Madhu B',
        'address': 'Eurofins IT Solutions India Pvt Ltd., 1st Floor, Maruti Platinum, Lakshminarayana Pura, AECS Layou',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560037',
        'state_code': '29'
    },
    'shipping_details': {
        'name': 'Madhu B',
        'address': 'Eurofins IT Solutions India Pvt Ltd., 1st Floor, Maruti Platinum, Lakshminarayana Pura, AECS Layou',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560037',
        'state_code': '29'
    },
    'place_of_delivery': 'Karnataka',
    'order_details': {
        'order_no': '403-3225714-7676307',
        'order_date': '28.10.2019'
    },
    'invoice_details': {
        'invoice_no': 'KA-310565025-1920',
        'invoice_date': '28.10.2019',
        'reverse_charge': 'No'
    },
    'items': [
        {
            'description': 'Varasiddhi Silks Men\'s Formal Shirt (SH-05-42, Navy Blue, 42)',
            'unit_price': 338.10,
            'quantity': 1,
        },
        {
            'description': 'Varasiddhi Silks Men\'s Formal Shirt (SH-05-40, Navy Blue, 40)',
            'unit_price': 338.10,
            'quantity': 1,
        },
    ],
    'signature_image': 'ok.png'  
}

create_invoice(invoice_data)