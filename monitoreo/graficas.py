import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

LOG_PATTERN = re.compile(r"^03_nvidia_(\d{8})_(\d{4})\.txt$")
TIMESTAMP_RE = re.compile(r"^Timestamp:\s*(.+)$")
METRIC_RE = re.compile(r"^\s*([^:]+):\s*([0-9.,]+)\s*(.*)$")

METRIC_KEYS = {
    'GPU Current Temp': 'gpu_temp_c',
    'GPU Utilization': 'gpu_util_pct',
    'Memory Utilization': 'memory_util_pct',
    'Instantaneous Power Draw': 'power_w',
    'Graphics Clock': 'graphics_clock_mhz',
    'Memory Clock': 'memory_clock_mhz',
}

PLOT_CONFIGS = [
    ('gpu_temp_c', 'GPU Temperature (C)'),
    ('gpu_util_pct', 'GPU Utilization (%)'),
    ('memory_util_pct', 'Memory Utilization (%)'),
    ('power_w', 'Power Draw (W)'),
    ('graphics_clock_mhz', 'Graphics Clock (MHz)'),
    ('memory_clock_mhz', 'Memory Clock (MHz)'),
]


def parse_log_file(path: Path):
    data = {'timestamp': None}
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.lstrip('\ufeff')
            if data['timestamp'] is None:
                m = TIMESTAMP_RE.match(line)
                if m:
                    data['timestamp'] = datetime.strptime(m.group(1).strip(), '%Y-%m-%d %H:%M:%S')
                    continue

            m = METRIC_RE.match(line)
            if not m:
                continue

            name = m.group(1).strip()
            value = m.group(2).replace(',', '.')
            unit = m.group(3).strip()

            if name in METRIC_KEYS:
                key = METRIC_KEYS[name]
                try:
                    data[key] = float(value)
                except ValueError:
                    pass

    return data if data['timestamp'] else None


def collect_series(log_dir: Path):
    records = []
    for path in sorted(log_dir.glob('03_nvidia_*.txt')):
        record = parse_log_file(path)
        if record:
            records.append(record)

    records.sort(key=lambda item: item['timestamp'])
    return records


def save_plots(records, output_dir: Path):
    if not records:
        print('No valid log records found to plot.')
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    times = [record['timestamp'] for record in records]

    for key, label in PLOT_CONFIGS:
        values = [record.get(key) for record in records]
        if all(v is None for v in values):
            continue

        plt.figure(figsize=(10, 5))
        plt.plot(times, values, marker='o', linestyle='-', color='tab:blue')
        plt.title(label)
        plt.xlabel('Time')
        plt.ylabel(label)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        filename = output_dir / f'{key}.png'
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f'Generated plot: {filename}')

    if output_dir.exists():
        print(f'Plots saved to: {output_dir}')


def save_csv(records, output_dir: Path):
    if not records:
        return

    csv_path = output_dir / '03_nvidia_series.csv'
    keys = ['timestamp'] + [key for key, _ in PLOT_CONFIGS]
    with csv_path.open('w', encoding='utf-8') as f:
        f.write(','.join(keys) + '\n')
        for record in records:
            row = [record.get(key, '') for key in keys]
            row = [r.isoformat() if isinstance(r, datetime) else str(r) for r in row]
            f.write(','.join(row) + '\n')

    print(f'CSV export saved to: {csv_path}')


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    log_dir = base_dir
    output_dir = base_dir / 'plots'

    print(f'Reading logs from: {log_dir}')
    records = collect_series(log_dir)
    print(f'Found {len(records)} log records.')

    if not records:
        raise SystemExit('No log records were found in the directory.')

    save_plots(records, output_dir)
    save_csv(records, output_dir)
