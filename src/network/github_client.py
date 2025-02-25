import json
import os
from datetime import datetime
from typing import Dict, Any
import base64
from github import Github, InputGitTreeElement
from github.Repository import Repository


class GitHubClient:
    """Класс для работы с GitHub Pages."""

    def __init__(self, token: str, repo_name: str):
        """
        Инициализация клиента.
        
        Args:
            token: GitHub Personal Access Token
            repo_name: Имя репозитория (формат: username/repo)
        """
        self.github = Github(token)
        self.repo: Repository = self.github.get_repo(repo_name)

    def upload_heatmap(self, file_path: str) -> Dict[str, Any]:
        """
        Загрузить тепловую карту на GitHub Pages.
        
        Args:
            file_path: Путь к JSON файлу с данными
        
        Returns:
            Dict с информацией о загруженной карте
        """
        # Читаем данные из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Генерируем уникальный ID для карты
        heatmap_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем метаданные для карты
        metadata = {
            "id": heatmap_id,
            "name": os.path.basename(file_path),
            "created": datetime.now().isoformat(),
            "resolution": data['resolution']
        }

        try:
            # Получаем текущий список карт
            try:
                heatmaps_content = self.repo.get_contents(
                    "data/heatmaps.json",
                    ref="gh-pages"
                )
                heatmaps_data = json.loads(base64.b64decode(heatmaps_content.content))
            except:
                heatmaps_data = {"heatmaps": []}

            # Добавляем новую карту в список
            heatmaps_data["heatmaps"].append(metadata)

            # Создаем новые файлы
            files = {
                "data/heatmaps.json": json.dumps(heatmaps_data, indent=2),
                f"data/maps/{heatmap_id}.json": json.dumps(data, indent=2)
            }

            # Получаем текущее дерево
            ref = self.repo.get_git_ref("heads/gh-pages")
            commit = self.repo.get_git_commit(ref.object.sha)
            tree = self.repo.get_git_tree(commit.tree.sha)

            # Создаем элементы дерева
            tree_elements = []
            for path, content in files.items():
                blob = self.repo.create_git_blob(content, "utf-8")
                tree_elements.append(InputGitTreeElement(
                    path=path,
                    mode="100644",
                    type="blob",
                    sha=blob.sha
                ))

            # Создаем новое дерево и коммит
            new_tree = self.repo.create_git_tree(tree_elements, tree)
            new_commit = self.repo.create_git_commit(
                f"Добавлена тепловая карта {heatmap_id}",
                new_tree,
                [commit]
            )

            # Обновляем ветку gh-pages
            ref.edit(new_commit.sha)

            return metadata

        except Exception as e:
            raise Exception(f"Ошибка при загрузке на GitHub: {str(e)}")

    def get_heatmap_url(self, heatmap_id: str) -> str:
        """Получить URL тепловой карты."""
        return f"https://fylhtq7779.github.io/HeatMapCAD_DV/data/maps/{heatmap_id}.json" 