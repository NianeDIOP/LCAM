import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_distribution_moyennes(df, title="Distribution des moyennes", column="Moy"):
    """
    Crée un histogramme de distribution des moyennes
    
    Args:
        df: DataFrame contenant une colonne de moyennes
        title: Titre du graphique
        column: Nom de la colonne à utiliser pour l'axe x
    
    Returns:
        fig: Figure Plotly
    """
    fig = px.histogram(
        df, 
        x=column, 
        nbins=20,
        color_discrete_sequence=['#3498db'],
        title=title
    )
    
    fig.update_layout(
        xaxis_title="Moyenne",
        yaxis_title="Nombre d'élèves",
        bargap=0.1
    )
    
    return fig

def plot_repartition_par_sexe(df, column="Moy", title="Répartition par sexe"):
    """
    Crée un graphique en boîte des moyennes par sexe
    
    Args:
        df: DataFrame contenant des colonnes 'Sexe' et une colonne de valeurs
        column: Nom de la colonne à analyser
        title: Titre du graphique
    
    Returns:
        fig: Figure Plotly
    """
    # Support both lowercase and proper case column
    df_copy = df.copy()
    if 'sexe' in df_copy.columns:
        df_copy.rename(columns={'sexe': 'Sexe'}, inplace=True)
    if 'Sexe' not in df_copy.columns:
        st.warning("La colonne 'Sexe' n'est pas disponible dans les données.")
        return None
    # Remplacer les valeurs de sexe pour plus de clarté
    df_copy['Sexe'] = df_copy['Sexe'].replace({'M': 'Garçons', 'F': 'Filles'})
    
    fig = px.box(
        df_copy, 
        x="Sexe", 
        y=column,
        color="Sexe",
        title=title,
        color_discrete_map={'Garçons': '#3498db', 'Filles': '#e74c3c'}
    )
    
    fig.update_layout(
        xaxis_title="Sexe",
        yaxis_title=column
    )
    
    return fig

def plot_comparaison_disciplines(df, disciplines, title="Comparaison des disciplines"):
    """
    Crée un graphique radar pour comparer les moyennes par discipline
    
    Args:
        df: DataFrame contenant les moyennes par discipline
        disciplines: Liste des disciplines à inclure
        title: Titre du graphique
    
    Returns:
        fig: Figure Plotly
    """
    # Calculer les moyennes par discipline
    moyennes = []
    for discipline in disciplines:
        if discipline in df.columns:
            moyennes.append(df[discipline].mean())
        else:
            moyennes.append(0)  # Valeur par défaut si la discipline n'est pas trouvée
    
    # Créer le graphique radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=moyennes,
        theta=disciplines,
        fill='toself',
        name='Moyenne classe',
        line_color='#3498db'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 20]  # Note maximale
            )
        ),
        title=title
    )
    
    return fig

def plot_evolution_semestres(df_s1, df_s2, title="Évolution entre les deux semestres"):
    """
    Crée un graphique pour comparer les moyennes entre S1 et S2
    
    Args:
        df_s1: DataFrame contenant les moyennes du S1
        df_s2: DataFrame contenant les moyennes du S2
        title: Titre du graphique
    
    Returns:
        fig: Figure Plotly
    """
    # Fusionner les données
    df_merged = pd.merge(
        df_s1[['IEN', 'Moy']], 
        df_s2[['IEN', 'Moy']], 
        on='IEN', 
        suffixes=('_S1', '_S2')
    )
    
    # Calculer la progression
    df_merged['Evolution'] = df_merged['Moy_S2'] - df_merged['Moy_S1']
    
    # Créer le graphique
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_merged['IEN'],
        y=df_merged['Evolution'],
        marker_color=['#2ecc71' if x >= 0 else '#e74c3c' for x in df_merged['Evolution']],
        name='Évolution'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Élèves (IEN)",
        yaxis_title="Évolution (points)",
        xaxis=dict(
            tickmode='array',
            tickvals=df_merged['IEN'],
            ticktext=[f"Élève {i+1}" for i in range(len(df_merged))]
        )
    )
    
    return fig

def generer_tableau_honneur(df, n=10):
    """
    Génère un tableau d'honneur des n meilleurs élèves
    
    Args:
        df: DataFrame contenant les moyennes et rangs
        n: Nombre d'élèves à inclure
    
    Returns:
        df_honneur: DataFrame des n meilleurs élèves
    """
    df_honneur = df.sort_values('Moy', ascending=False).head(n)
    
    # Sélectionner les colonnes pertinentes
    colonnes = ['Prénom', 'Nom', 'Moy', 'Rang']
    if 'Sexe' in df.columns:
        colonnes.insert(2, 'Sexe')
    
    return df_honneur[colonnes]