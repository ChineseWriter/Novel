call .\.venv\Scripts\activate.bat
cd .\r_lib
maturin develop --skip-install
cd ..
move .\r_lib\target\debug\r_lib.pdb .\downloader\r_lib.pdb
pause