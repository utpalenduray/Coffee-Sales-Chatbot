from functions import connect_sql_lite_db, clean_sql_query
import pandas as pd
import matplotlib.pyplot as plt
from langchain_core.tools import tool

@tool
def execute_sql_query(query: str):
    """
    Executes an SQL query on an SQLite database.
    Args:
        query (str): The SQL query to execute.

    Returns:
        dict: A dictionary containing the result of the query.
    """
    connection, cursor = connect_sql_lite_db("coffee_sales_database.db")
    cursor.execute(clean_sql_query(query))
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])
    cursor.close()
    connection.close()
    return df.to_dict(orient="list")

@tool
def plot_graph(graph_data, graph_type, graph_title, ylabel, xlabel):
    """
    Plots a graph based on the graph_data provided.
    Args:
        graph_data (dict): A dictionary containing the data to be plotted.
        graph_type (str): The type of graph to be plotted i.e, bar or line.
        graph_title (str): The title of the graph.
        ylabel (str): The label for the y-axis.
        xlabel (str): The label for the x-axis.

    Returns:
        None
    """
    if 'month' not in graph_data:
        raise ValueError("Input data must contain a 'month' key.")

    months = graph_data['month']

    if graph_type=='line':
        for key, values in graph_data.items():
            if key == 'month':
                continue
            plt.plot(months, values, marker='o', label=key)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(graph_title)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"graph_images/test_image.jpg")