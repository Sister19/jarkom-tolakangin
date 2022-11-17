# IF3130 - Jaringan Komputer 2022 - TolakAngin
Tugas Besar 2 IF3130 Jaringan Komputer

Dibuat oleh:
- 13520002 - Muhammad Fikri Ranjabi
- 13520017 - Diky Restu Maulana
- 13520122 - Alifia Rahmah

## Deskripsi

Sebuah simulasi jaringan TCP menggunakan UDP dengan Python. Simulasi meliputi pembuatan segment, pengiriman segment menggunakan socket, dan validasi segment yang diterima. Program ini dibuat untuk memenuhi Tugas Besar 2 IF3130 - Jaringan Komputer 2022.

## Cara Penggunaan

### Server

1. Jalankan server dengan perintah `python3 server.py <server_port> <filename>`.
2. Server akan menunggu koneksi dari client.
3. Jika client terhubung, server akan mengirimkan file yang diminta oleh client.

### Client
1. Jalankan client dengan perintah `python3 client.py <client_port> <server_port> <filename>`.
2. Client akan mengirimkan request ke server.
3. Jika server mengirimkan file, client akan menyimpan file tersebut.

## Pembagian Tugas

- Muhammad Fikri Ranjabi (13520002): Implementasi client-server, file transfer, three way handshake
- Diky Restu Maulana (13520017): Implementasi Go-Back-N ARQ
- Alifia Rahmah (13520122): Pembuatan struktur segment dan connection
