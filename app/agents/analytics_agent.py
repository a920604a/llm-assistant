import pandas as pd
import matplotlib.pyplot as plt

# 假設有結構化表格資訊輸入

def summarize_table(data):
    df = pd.DataFrame(data)
    return df.describe().to_dict()


def generate_chart(df, output_path="chart.png"):
    df.plot(kind="bar")
    plt.tight_layout()
    plt.savefig(output_path)