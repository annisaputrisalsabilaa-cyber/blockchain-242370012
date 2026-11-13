from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from pathlib import Path
import hashlib
import json
import html
# Menyimpan data block
blocks = []
class BlockchainServer(BaseHTTPRequestHandler):
    # Menampilkan halaman website
    def do_GET(self):
        self.tampilkan_halaman()
    # Menerima data dari HTML
    def do_POST(self):
        panjang = int(self.headers['Content-Length'])
        data = self.rfile.read(panjang).decode('utf-8')
        form = parse_qs(data)
        nama1 = form.get('nama1', [''])[0]
        nama2 = form.get('nama2', [''])[0]
        uang = form.get('uang', [''])[0]
        # Memeriksa pilihan nama
        if nama1 not in ['Ali', 'Tono'] or nama2 not in ['Ali', 'Tono']:
            self.send_error(400, "Nama tidak valid")
            return
        # Memeriksa jumlah uang
        try:
            uang = int(uang.replace(",", "").replace(".", ""))
            if uang < 1:
                raise ValueError
        except ValueError:
            self.send_error(400, "Jumlah uang tidak valid")
            return
        # Membuat nomor block
        nomor = len(blocks)
        # Membuat data block
        data_block = {
            "nomor": nomor,
            "nama1": nama1,
            "nama2": nama2,
            "uang": uang
        }
        # Mengubah data menjadi JSON
        isi_data = json.dumps(
            data_block,
            sort_keys=True
        )
        # Membuat Hash SHA-256
        hash_block = hashlib.sha256(
            isi_data.encode('utf-8')
        ).hexdigest()
        # Memasukkan hash ke dalam block
        data_block["hash"] = hash_block
        # Menyimpan block
        blocks.append(data_block)
        # Mengarahkan kembali ke halaman utama
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()
    # Menampilkan hasil block
    def tampilkan_halaman(self):
        # Membaca file HTML
        file_html = Path(__file__).parent / "index.html"
        halaman = file_html.read_text(encoding="utf-8")
        # Menyiapkan hasil output
        hasil = ""
        for block in blocks:
            hasil += f"""
            <div class="block">
                <h3>Block {block['nomor']}</h3>
                <p>Nama 1: {html.escape(block['nama1'])}</p>
                <p>Nama 2: {html.escape(block['nama2'])}</p>
                <p>Uang: {block['uang']:,}</p>
                <p>Hash:</p>
                <p>{block['hash']}</p>
            </div>
            """
        # Jika belum ada data
        if hasil == "":
            hasil = "<p>Belum ada data.</p>"
        # Memasukkan hasil ke HTML
        halaman = halaman.replace(
            "{{BLOCKS}}",
            hasil
        )
        # Mengirim halaman ke browser
        isi = halaman.encode("utf-8")
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(isi))
        )
        self.end_headers()
        self.wfile.write(isi)
# Menjalankan server localhost
server = HTTPServer(
    ("127.0.0.1", 8080),
    BlockchainServer
)
print("Server berjalan di http://localhost:8080")
server.serve_forever()
