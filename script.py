from woocommerce import API

wcapi = API(
    url="http://mundoimportado.store",
    consumer_key="ck_54ca9069813af476ba77be678ee66dee429e8e4c",
    consumer_secret="cs_0cbe30dfc27fd0871d9ddc690b6baf86a88897cf",
    wp_api=True,
    version="wc/v3"
)

# Obtener órdenes
response = wcapi.get("orders", params={"per_page": 100})  # Ajusta el número según necesites

if response.status_code == 200:
    orders = response.json()
    
    for order in orders:
        # Información básica del pedido
        print(f"\n{'='*50}")
        print(f"📦 Pedido ID: {order['id']}")
        print(f"👤 Cliente: {order['billing']['first_name']} {order['billing']['last_name']}")
        print(f"📞 Teléfono: {order['billing']['phone']}")
        print(f"📦 status: {order['status']}")
        print(f"🛒 Productos:")
        
        # Detalles de cada producto
        for item in order['line_items']:
            print(f"  - {item['name']} (ID: {item['product_id']})")
            print(f"    Cantidad: {item['quantity']}")
            print(f"    Precio unitario: ${float(item['price']):.2f}")
            print(f"    Total: ${float(item['total']):.2f}")
        
        print(f"{'='*50}\n")
else:
    print(f"Error al obtener órdenes. Código: {response.status_code}")
    print(response.text)