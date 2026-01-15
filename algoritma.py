import re
import time

# --- BAGIAN 1: PREPROCESSING ---
def preprocess_text(text):
    # Case folding
    text = text.lower()
    # Hapus karakter non-alphanumeric (simbol aneh, emoji, dll)
    # Ini langkah pencegahan pertama agar karakter aneh hilang
    text = re.sub(r'[^\w\s]', '', text)
    return text

def split_sentences(text):
    # Memecah berdasarkan titik atau baris baru
    sentences = re.split(r'[.\n]+', text)
    return [s.strip() for s in sentences if s.strip()]

# --- BAGIAN 2: ALGORITMA KMP (Tidak Ada Perubahan) ---
def compute_lps_array(pattern, M, lps):
    length = 0
    lps[0] = 0
    i = 1
    while i < M:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

def kmp_search(pattern, text):
    M = len(pattern)
    N = len(text)
    lps = [0] * M
    compute_lps_array(pattern, M, lps)
    
    i = 0 
    j = 0
    while i < N:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == M:
            return True
        elif i < N and pattern[j] != text[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return False

# --- BAGIAN 3: ALGORITMA BOYER-MOORE (REVISI DICTIONARY) ---
def bad_char_heuristic(string, size):
    bad_char = {} 
    
    for i in range(size):
        # Simpan posisi terakhir karakter
        bad_char[string[i]] = i
        
    return bad_char

def boyer_moore_search(pattern, text):
    m = len(pattern)
    n = len(text)
    
    # Panggil fungsi heuristic yang baru
    bad_char = bad_char_heuristic(pattern, m)
    
    s = 0
    while s <= n - m:
        j = m - 1
        
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
            
        if j < 0:
            return True # Pola ditemukan
        else:
            shift_bad_char = bad_char.get(text[s + j], -1)
            
            s += max(1, j - shift_bad_char)
            
    return False

# --- FUNGSI UTAMA ---
def calculate_similarity(doc_suspect, doc_original, algorithm="KMP"):
    start_time = time.time()
    
    # 1. Preprocessing Dokumen Asli
    clean_original = preprocess_text(doc_original)
    
    # 2. Ambil pola dari Suspect
    raw_patterns = split_sentences(doc_suspect)
    
    # 3. Filtering: Hanya ambil kalimat yang cukup panjang (>= 3 huruf)
    valid_patterns = [p for p in raw_patterns if len(p) >= 3]
    
    if not valid_patterns: 
        return 0.0, 0.0, []
    
    matches = 0
    detected_sentences = []
    
    for pattern in valid_patterns:
        is_found = False
        
        # Preprocess pola juga
        clean_pattern = preprocess_text(pattern)
        
        # Validasi lagi setelah dibersihkan
        if len(clean_pattern) < 3:
            continue

        # Pilih Algoritma
        if algorithm == "KMP":
            is_found = kmp_search(clean_pattern, clean_original)
        else: # Boyer-Moore
            is_found = boyer_moore_search(clean_pattern, clean_original)
            
        if is_found:
            matches += 1
            detected_sentences.append({
                "Kalimat Terdeteksi": pattern,
                "Status": "Plagiat"
            })
            
    execution_time = time.time() - start_time
    percentage = (matches / len(valid_patterns)) * 100
    
    return percentage, execution_time, detected_sentences