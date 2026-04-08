# 🎬 YouTube HD Downloader

Um aplicativo desktop desenvolvido em Python com interface gráfica (CustomTkinter) para baixar vídeos e áudios do YouTube de forma simples e rápida.

## 🚀 Como Usar

1. Cole a **URL do vídeo** do YouTube no campo indicado.
2. Clique no botão **🔍 Obter Informações**.
3. Em Tipo de Download, selecione **'Vídeo HD (1080p+)'**.
4. Escolha a resolução desejada (ex: **'1080p'** ou **'Melhor disponível'**).
5. Selecione a pasta de destino e clique em **⬇️ Baixar em HD**.

> **⚠️ Nota Importante:** Alguns vídeos em 1080p ou resoluções superiores podem não estar disponíveis como *streams* progressivos nativos do YouTube (onde áudio e vídeo vêm juntos no mesmo arquivo). Nesses casos, o aplicativo baixará o arquivo de vídeo na melhor qualidade visual disponível.

## 🛠️ Instalação e Execução

Certifique-se de ter o Python instalado e instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
