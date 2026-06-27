const API_URL = 'REPLACE_WITH_API_URL';

async function fetchImages() {
  try {
    const res    = await fetch(API_URL + '/images');
    const images = await res.json();
    renderGallery(images);
  } catch (e) {
    document.getElementById('gallery').innerHTML =
      '<div class="empty">Failed to load images</div>';
  }
}

function renderGallery(images) {
  const gallery = document.getElementById('gallery');

  if (!images.length) {
    gallery.innerHTML = '<div class="empty">No images yet. Upload one!</div>';
    return;
  }

  gallery.innerHTML = images.map(img => `
    <div class="card" onclick="openModal(${JSON.stringify(img).replace(/"/g, '&quot;')})">
      <img src="${img.urls?.thumbnail}" alt="${img.filename}">
      <div class="card-info">
        <div class="card-name">${img.filename}</div>
        <div class="card-date">${new Date(img.created_at).toLocaleDateString('en-GB')}</div>
        <div class="badges">
          <span class="badge">thumbnail</span>
          <span class="badge">medium</span>
          <span class="badge">large</span>
        </div>
      </div>
    </div>
  `).join('');
}

function openModal(img) {
  document.getElementById('modal-title').textContent = img.filename;
  document.getElementById('modal-img').src = img.urls?.large || img.urls?.medium;
  document.getElementById('download-row').innerHTML = Object.entries(img.urls || {})
    .map(([size, url]) => `<a href="${url}" class="download-btn" download>↓ ${size}</a>`)
    .join('');
  document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('modal').style.display = 'none';
}

document.getElementById('modal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

document.getElementById('file-input').addEventListener('change', async function(e) {
  const file = e.target.files[0];
  if (!file) return;

  const label  = document.getElementById('upload-label');
  const status = document.getElementById('status-bar');

  label.textContent    = 'Uploading...';
  status.style.display = 'block';
  status.textContent   = '⏳ Uploading image...';

  try {
    const res            = await fetch(API_URL + '/upload', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ filename: file.name })
    });
    const { upload_url } = await res.json();

    const form = new FormData();
    Object.entries(upload_url.fields).forEach(([k, v]) => form.append(k, v));
    form.append('file', file);

    await fetch(upload_url.url, { method: 'POST', body: form });

    status.textContent = '✅ Uploaded! Processing...';

    setTimeout(() => {
      fetchImages();
      status.textContent = '✅ Done! Image processed in 3 sizes.';
      label.textContent  = '+ Upload Image';
      setTimeout(() => { status.style.display = 'none'; }, 3000);
    }, 4000);

  } catch (e) {
    status.textContent = '❌ Upload failed. Try again.';
    label.textContent  = '+ Upload Image';
  }
});

fetchImages();
