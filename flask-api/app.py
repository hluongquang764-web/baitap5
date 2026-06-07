import os
import time
import pymysql
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host":   os.getenv("DB_HOST", "bt5-mariadb"),
    "port":   int(os.getenv("DB_PORT", 3306)),
    "db":     os.getenv("DB_NAME", "petrol_db"),
    "user":   os.getenv("DB_USER", "petrol_user"),
    "passwd": os.getenv("DB_PASS", "petrol123"),
    "charset": "utf8mb4",
}

def get_db():
    for i in range(5):
        try:
            return pymysql.connect(**DB_CONFIG)
        except Exception as e:
            print(f"[DB] Retry {i+1}/5: {e}")
            time.sleep(3)
    raise RuntimeError("Không thể kết nối MariaDB")

def classify(price, fuel_type):
    """
    Ngưỡng cảnh báo (VNĐ/lít):
      RON95 : < 20000 LOW | 20000-25000 OK | > 25000 HIGH
      RON92 : < 19000 LOW | 19000-24000 OK | > 24000 HIGH
      DO    : < 18000 LOW | 18000-23000 OK | > 23000 HIGH
    """
    thresholds = {
        'RON95-III': (20000, 25000),
        'RON92-II':  (19000, 24000),
        'DO 0.05S':  (18000, 23000),
    }
    low, high = thresholds.get(fuel_type, (19000, 25000))
    if price == 0:   return "NO_DATA"
    if price < low:  return "ALERT_LOW"
    if price > high: return "ALERT_HIGH"
    return "OK"

@app.route("/api/petrol", methods=["GET"])
def get_petrol():
    try:
        conn = get_db()
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT fuel_type, price, unit, updated_at "
                "FROM petrol_price ORDER BY id"
            )
            rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "fuel_type":  r["fuel_type"],
                "price":      int(r["price"]),
                "unit":       r["unit"],
                "updated_at": str(r["updated_at"]),
                "status":     classify(int(r["price"]), r["fuel_type"])
            })
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
