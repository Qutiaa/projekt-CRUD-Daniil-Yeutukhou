const apiUrl = '/products';

// Очищаем все ошибки
function clearErrors() {
  ['name','category','price','quantity','date_added'].forEach(f => {
    const el = document.getElementById('error-' + f);
    if (el) el.textContent = '';
  });
}

// Получаем продукты и заполняем таблицу
async function fetchProducts() {
  const res = await fetch(apiUrl);
  const products = await res.json();
  const tbody = document.getElementById('productsTable');
  tbody.innerHTML = '';
  products.forEach(p => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${p.id}</td>
      <td contenteditable="true">${p.name}</td>
      <td contenteditable="true">${p.category}</td>
      <td contenteditable="true">${p.price}</td>
      <td contenteditable="true">${p.quantity}</td>
      <td contenteditable="true">${p.date_added}</td>
      <td>
        <button onclick="updateProduct(${p.id}, this)" class="update">Aktualizacja</button>
        <button onclick="deleteProduct(${p.id})" class="delete">Usuwac</button>
      </td>`;
    tbody.appendChild(row);
  });
}

// Добавляем продукт с отображением ошибок под полями
async function addProduct() {
  clearErrors();

  const data = {
    name: document.getElementById('name').value,
    category: document.getElementById('category').value,
    price: parseFloat(document.getElementById('price').value),
    quantity: parseInt(document.getElementById('quantity').value),
    date_added: document.getElementById('date_added').value
  };

  const res = await fetch(apiUrl, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  });

  const result = await res.json();

  if (!res.ok) {
    if (result.fieldErrors) {
      result.fieldErrors.forEach(e => {
        const el = document.getElementById('error-' + e.field);
        if (el) el.textContent = e.message;
      });
    } else {
      alert(result.error);
    }
    return;
  }

  // Очистка полей после успешного добавления
  ['name','category','price','quantity','date_added'].forEach(f => {
    document.getElementById(f).value = '';
  });

  fetchProducts();
}

// Редактируем продукт (ошибки пока alert)
async function updateProduct(id, btn) {
  clearErrors();

  const row = btn.parentElement.parentElement;
  const data = {
    name: row.cells[1].innerText,
    category: row.cells[2].innerText,
    price: parseFloat(row.cells[3].innerText),
    quantity: parseInt(row.cells[4].innerText),
    date_added: row.cells[5].innerText
  };

  const res = await fetch(`${apiUrl}/${id}`, {
    method: 'PUT',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  });

  const result = await res.json();

  if (!res.ok) {
    if (result.fieldErrors) {
      result.fieldErrors.forEach(e => {
        alert(`${e.field}: ${e.message}`);
      });
    } else {
      alert(result.error);
    }
    return;
  }

  fetchProducts();
}

// Удаляем продукт
async function deleteProduct(id) {
  await fetch(`${apiUrl}/${id}`, { method: 'DELETE' });
  fetchProducts();
}

// Начальная загрузка
fetchProducts();
