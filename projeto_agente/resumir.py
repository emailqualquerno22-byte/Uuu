import json
from collections import defaultdict

with open("vendas.json", "r", encoding="utf-8") as f:
    vendas = json.load(f)

total_faturado = 0.0
total_itens = 0
mais_vendido = None
maior_quantidade = 0
detalhes = []

for venda in vendas:
    produto = venda["produto"]
    quantidade = int(venda["quantidade"])
    preco_unitario = float(venda["preco_unitario"])
    subtotal = quantidade * preco_unitario
    total_faturado += subtotal
    total_itens += quantidade
    detalhes.append((produto, quantidade, preco_unitario, subtotal))
    if quantidade > maior_quantidade:
        maior_quantidade = quantidade
        mais_vendido = produto

ticket_medio = total_faturado / len(vendas) if vendas else 0.0

print("=== Resumo de Vendas ===")
for produto, quantidade, preco_unitario, subtotal in detalhes:
    print(f"{produto}: {quantidade} x {preco_unitario:.2f} = {subtotal:.2f}")
print(f"\nTotal faturado: {total_faturado:.2f}")
print(f"Item mais vendido: {mais_vendido} ({maior_quantidade} unidades)")
print(f"Ticket medio: {ticket_medio:.2f}")
