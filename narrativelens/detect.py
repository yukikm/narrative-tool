from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from .io import Item


@dataclass
class DetectParams:
    k_min: int = 2
    k_max: int = 8
    recent_days: int = 3
    max_features: int = 6000
    ngram_max: int = 2
    min_df: int = 2
    score_volume_weight: float = 0.55
    score_trend_weight: float = 0.45


def _pick_k(x, k_min: int, k_max: int, random_state: int = 42) -> int:
    # If dataset is small, clamp.
    n = x.shape[0]
    k_max = min(k_max, max(k_min, n - 1))
    if k_max <= k_min:
        return max(2, min(k_min, n - 1))

    best_k = k_min
    best_score = -1.0

    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        labels = km.fit_predict(x)
        # silhouette requires at least 2 clusters and no cluster with 1 item ideally
        try:
            s = float(silhouette_score(x, labels))
        except Exception:
            s = -1.0
        if s > best_score:
            best_score = s
            best_k = k
    return best_k


def detect_narratives(items: list[Item], params: DetectParams) -> dict[str, Any]:
    if not items:
        raise ValueError("No items provided")

    docs = [it.doc for it in items]

    vec = TfidfVectorizer(
        stop_words="english",
        max_features=params.max_features,
        ngram_range=(1, params.ngram_max),
        min_df=params.min_df,
    )
    x = vec.fit_transform(docs)

    k = _pick_k(x, params.k_min, params.k_max)
    km = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = km.fit_predict(x)

    # Cluster keywords
    feature_names = np.array(vec.get_feature_names_out())
    centroids = km.cluster_centers_

    now = max(it.created_at for it in items).astimezone(timezone.utc)
    recent_cut = now - timedelta(days=params.recent_days)

    narratives: list[dict[str, Any]] = []
    for c in range(k):
        idxs = np.where(labels == c)[0].tolist()
        if not idxs:
            continue

        # top keywords
        top_idx = np.argsort(centroids[c])[::-1][:12]
        keywords = [str(feature_names[i]) for i in top_idx if centroids[c][i] > 0]
        keywords = keywords[:8]

        cluster_items = [items[i] for i in idxs]
        cluster_items.sort(key=lambda it: it.created_at, reverse=True)

        volume = len(cluster_items)
        recent = sum(1 for it in cluster_items if it.created_at >= recent_cut)
        baseline = max(1, volume - recent)
        trend_ratio = recent / baseline  # >1 means accelerating

        # Score: log-volume + capped trend
        vol_score = float(np.log1p(volume))
        trend_score = float(min(3.0, trend_ratio))
        score = params.score_volume_weight * vol_score + params.score_trend_weight * trend_score

        examples = [
            {
                "id": it.id,
                "created_at": it.created_at.isoformat(),
                "source": it.source,
                "title": it.title,
                "url": it.url,
            }
            for it in cluster_items[:5]
        ]

        narratives.append(
            {
                "cluster_id": int(c),
                "name": ", ".join(keywords[:3]) if keywords else f"cluster-{c}",
                "keywords": keywords,
                "volume": volume,
                "recent": recent,
                "recent_days": params.recent_days,
                "trend_ratio": trend_ratio,
                "score": score,
                "examples": examples,
            }
        )

    narratives.sort(key=lambda n: n["score"], reverse=True)

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "item_count": len(items),
        "params": {
            **params.__dict__,
            "picked_k": k,
        },
        "narratives": narratives,
    }
