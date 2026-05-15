import subprocess
import json

input_cameras = [
    ("Buxoro portal asosiy kirish",          "10.6.141.15"),
    ("Buxoro portal asosiy kirish",          "10.6.141.13"),
    ("Buxoro portal asosiy kirish",          "10.6.141.12"),
    ("Buxoro portal asosiy kirish",          "10.6.141.10"),
    ("Buxoro portal kirish 1-etaj",          "10.6.141.14"),
    ("Buxoro portal ko'chadan kirish 1",     "10.6.141.9"),
    ("Buxoro portal ko'chadan kirish 2",     "10.6.141.11"),
    ("Direksiya kirish zina",                "10.6.141.32"),
    ("Direksiya sokolniy",                   "10.6.141.33"),
    ("Ishchilar kirish qismi garajdan",      "10.6.141.30"),
    ("Monitoringga kirish",                  "10.6.141.25"),
    ("Monitoring zina",                      "10.6.141.24"),
    ("M.Ulug'bek portal 1-etaj 1",          "10.6.141.36"),
    ("M.Ulug'bek portal 1-etaj 2",          "10.6.141.36"),
    ("M.Ulug'bek portal asosiy kirish",      "10.6.141.48"),
    ("M.Ulug'bek portal asosiy kirish",      "10.6.141.39"),
    ("M.Ulug'bek portal kirish",             "10.6.141.40"),
    ("Qoqon portal kirish",                  "10.6.141.46"),
    ("Qoqon portal kirish",                  "10.6.141.45"),
    ("Qoqon portal kirish",                  "10.6.141.44"),
    ("Restavrasiyaga tushish",               "10.6.141.16"),
    ("Sokolniy B73",                         "10.6.141.28"),
    ("Sokolniy gruzavoyga tushish",          "10.6.141.29"),
    ("Tex.etaj ventelyasonniyga chiqish",    "10.6.141.26"),
    ("Ventilyasonniyga kirish",              "10.6.141.27"),
    ("Vintelyasionniy zina",                 "10.6.141.7"),
    ("Xorazm portal kirish",                 "10.6.141.43"),
    ("Xorazm portal kirish",                 "10.6.141.42"),
    ("Xorazm portal kirish",                 "10.6.141.41"),
]

output_cameras = [
    ("M.Ulug'bek portal 1-etaj 1",          "10.6.141.37"),
    ("M.Ulug'bek portal 1-etaj 2",          "10.6.141.37"),
    ("M.Ulug'bek portal chiqish",            "10.6.141.47"),
    ("M.Ulug'bek portal pojarniy chiqish",   "10.6.141.23"),
    ("M.Ulug'bek portal pojarniy chiqish",   "10.6.141.22"),
    ("Restavrasiyaga tushish",               "10.6.141.31"),
    ("Vintelyasionniy zina",                 "10.6.141.8"),
]

BASE_URL     = "https://172.20.20.9/lkvs-manager/v1/camera/face/detection-count"
REGION_SOATO = "1726"
FROM_DATE    = "16.02.2026 00:00:00"
TO_DATE      = "16.03.2026 23:59:59"
AUTH_TOKEN   = "8e713f659aad819ba5fa02353d8c913a"


def fetch_data(ip):
    from_enc = FROM_DATE.replace(" ", "%20").replace(":", "%3A")
    to_enc   = TO_DATE.replace(" ", "%20").replace(":", "%3A")
    url = f"{BASE_URL}?region_soato={REGION_SOATO}&ip_address={ip}&from={from_enc}&to={to_enc}"
    cmd = [
        "curl", "--location", "--insecure", url,
        "--header", f"Authorization: {AUTH_TOKEN}",
        "--header", "Content-Type: application/json",
        "--silent"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def print_section(title, cameras):
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)
    for name, ip in cameras:
        data = fetch_data(ip)
        print(f"{ip}")
        if data:
            print(json.dumps(data, indent=4, ensure_ascii=False))
        else:
            print("  Xato: javob o'qilmadi")
        print("")
    print()


print_section("INPUT", input_cameras)
print_section("OUTPUT", output_cameras)