import customtkinter as ctk
from tkinter import messagebox, filedialog
from pytubefix import YouTube
from pytubefix.exceptions import PytubeFixError, VideoUnavailable
import os
import threading
import re
import time
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("YouTube HD Downloader")
        self.window.geometry("800x1000")
        self.window.resizable(False, False)
        
        # Variáveis para controle de download
        self.downloading = False
        self.cancel_download = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Título
        title_label = ctk.CTkLabel(
            self.window,
            text="YouTube HD Downloader",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=15)
        
        # Frame para entrada de URL
        url_frame = ctk.CTkFrame(self.window)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            url_frame,
            text="URL do YouTube:",
            font=("Arial", 14)
        ).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Cole o link do vídeo aqui...",
            height=40,
            font=("Arial", 12)
        )
        self.url_entry.pack(pady=10, padx=10, fill="x")
        
        # Botões de ação
        button_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 10), padx=10, fill="x")
        
        paste_button = ctk.CTkButton(
            button_frame,
            text="📋 Colar",
            width=120,
            command=self.paste_from_clipboard,
            font=("Arial", 11)
        )
        paste_button.pack(side="left", padx=(0, 5))
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="🗑️ Limpar",
            width=120,
            fg_color="gray",
            hover_color="dark gray",
            command=self.clear_fields,
            font=("Arial", 11)
        )
        clear_button.pack(side="left")
        
        # Frame para informações do vídeo
        self.info_frame = ctk.CTkFrame(self.window)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Nenhum vídeo carregado. Cole uma URL e clique em 'Obter Informações'.",
            wraplength=550,
            justify="left",
            font=("Arial", 11),
            height=80
        )
        self.info_label.pack(pady=15, padx=15, fill="both", expand=True)
        
        # Frame para opções de download
        options_frame = ctk.CTkFrame(self.window)
        options_frame.pack(pady=10, padx=20, fill="x")
        
        # Tipo de download
        ctk.CTkLabel(
            options_frame,
            text="Tipo de Download:",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.download_type = ctk.StringVar(value="video_hd")
        
        type_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        type_frame.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        
        video_hd_radio = ctk.CTkRadioButton(
            type_frame,
            text="Vídeo HD (1080p+)",
            variable=self.download_type,
            value="video_hd",
            command=self.update_resolution_options,
            font=("Arial", 11)
        )
        video_hd_radio.pack(anchor="w", pady=(0, 5))
        
        video_sd_radio = ctk.CTkRadioButton(
            type_frame,
            text="Vídeo SD (até 720p)",
            variable=self.download_type,
            value="video_sd",
            command=self.update_resolution_options,
            font=("Arial", 11)
        )
        video_sd_radio.pack(anchor="w", pady=(0, 5))
        
        audio_radio = ctk.CTkRadioButton(
            type_frame,
            text="Somente Áudio (MP3)",
            variable=self.download_type,
            value="audio",
            command=self.update_resolution_options,
            font=("Arial", 11)
        )
        audio_radio.pack(anchor="w")
        
        # Resolução
        self.resolution_label = ctk.CTkLabel(
            options_frame,
            text="Resolução:",
            font=("Arial", 13, "bold")
        )
        self.resolution_label.pack(anchor="w", padx=10, pady=(5, 5))
        
        self.resolution_var = ctk.StringVar(value="1080p")
        self.resolution_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["1080p", "720p", "480p", "360p", "Melhor disponível"],
            variable=self.resolution_var,
            width=250,
            font=("Arial", 11)
        )
        self.resolution_menu.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Pasta de destino
        ctk.CTkLabel(
            options_frame,
            text="Pasta de Destino:",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 5))
        
        self.download_path = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads", "YouTube"))
        
        path_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        path_frame.pack(padx=20, pady=(0, 10), fill="x")
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.download_path,
            font=("Arial", 11)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ctk.CTkButton(
            path_frame,
            text="📂",
            width=45,
            command=self.browse_folder,
            font=("Arial", 12)
        )
        browse_button.pack(side="right")
        
        # Botões principais
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(pady=15)
        
        self.get_info_button = ctk.CTkButton(
            button_frame,
            text="🔍 Obter Informações",
            command=self.get_video_info,
            height=50,
            width=200,
            font=("Arial", 14, "bold")
        )
        self.get_info_button.pack(side="left", padx=5)
        
        self.download_button = ctk.CTkButton(
            button_frame,
            text="⬇️ Baixar em HD",
            command=self.start_download,
            height=50,
            width=200,
            font=("Arial", 14, "bold"),
            state="disabled",
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        self.download_button.pack(side="left", padx=5)
        
        # Botão de cancelar (inicialmente escondido)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=self.cancel_download_process,
            height=50,
            width=100,
            font=("Arial", 12),
            fg_color="red",
            hover_color="dark red",
            state="disabled"
        )
        
        # Frame de progresso
        self.progress_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Progresso: 0%",
            font=("Arial", 11)
        )
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=20)
        self.progress_bar.pack(pady=(5, 0), fill="x")
        self.progress_bar.set(0)
        
        # Informações de download
        self.download_info_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=("Arial", 10)
        )
        self.download_info_label.pack(anchor="w", pady=(2, 0))
        
        # Status detalhado
        self.status_label = ctk.CTkLabel(
            self.window,
            text="Pronto para começar",
            font=("Arial", 11, "italic")
        )
        self.status_label.pack(pady=(0, 10))
        
        # Variáveis de controle
        self.video_streams = None
        self.audio_streams = None
        self.yt = None
        self.available_resolutions = []
        self.current_download_thread = None
        
    def paste_from_clipboard(self):
        try:
            import pyperclip
            clipboard_text = pyperclip.paste()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, clipboard_text)
        except ImportError:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, "pip install pyperclip para colar automaticamente")
            
    def clear_fields(self):
        self.url_entry.delete(0, "end")
        self.info_label.configure(text="Nenhum vídeo carregado. Cole uma URL e clique em 'Obter Informações'.")
        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Progresso: 0%")
        self.download_info_label.configure(text="")
        self.status_label.configure(text="Pronto para começar")
        self.video_streams = None
        self.audio_streams = None
        self.yt = None
        self.available_resolutions = []
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
    
    def update_resolution_options(self):
        """Atualiza as opções de resolução baseadas no tipo de download"""
        download_type = self.download_type.get()
        
        if download_type == "audio":
            self.resolution_menu.configure(state="disabled")
        else:
            self.resolution_menu.configure(state="normal")
            if self.available_resolutions:
                # Filtrar resoluções baseadas no tipo
                if download_type == "video_sd":
                    # Apenas resoluções SD
                    resolutions = [r for r in self.available_resolutions if not any(x in r for x in ['1080', '1440', '2160'])]
                    resolutions.append("Melhor disponível")
                    self.resolution_menu.configure(values=resolutions)
                    if "720p" in resolutions:
                        self.resolution_var.set("720p")
                else:
                    # Todas as resoluções
                    self.resolution_menu.configure(values=self.available_resolutions + ["Melhor disponível"])
                    if "1080p" in self.available_resolutions:
                        self.resolution_var.set("1080p")
    
    def get_video_info(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube")
            return
        
        # Validar URL do YouTube
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|shorts/|.+\?v=)?([^&=%\?]{11})'
        if not re.match(youtube_regex, url):
            messagebox.showerror("Erro", "URL do YouTube inválida!")
            return
        
        try:
            self.get_info_button.configure(state="disabled", text="Analisando...")
            self.status_label.configure(text="Conectando ao YouTube e analisando streams disponíveis...")
            self.progress_bar.set(0)
            
            # Usar threading para não travar a interface
            thread = threading.Thread(target=self._fetch_video_info, args=(url,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.get_info_button.configure(state="normal", text="🔍 Obter Informações")
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def _fetch_video_info(self, url):
        try:
            # Criar objeto YouTube com callbacks
            def progress_callback(stream, chunk, bytes_remaining):
                # Esta função será usada durante o download
                pass
            
            def complete_callback(stream, file_path):
                # Esta função será usada quando o download completar
                pass
            
            self.yt = YouTube(
                url,
                on_progress_callback=progress_callback,
                on_complete_callback=complete_callback
            )
            
            # Verificar disponibilidade
            self.yt.check_availability()
            
            # Obter TODOS os streams disponíveis
            all_streams = self.yt.streams
            
            # Coletar todas as resoluções disponíveis
            all_resolutions = set()
            
            # Resoluções dos streams progressivos (vídeo + áudio juntos)
            progressive_streams = all_streams.filter(progressive=True)
            for stream in progressive_streams:
                if stream.resolution:
                    all_resolutions.add(stream.resolution)
            
            # Resoluções dos streams adaptativos (apenas vídeo - HD)
            adaptive_video_streams = all_streams.filter(adaptive=True, only_video=True)
            for stream in adaptive_video_streams:
                if stream.resolution:
                    all_resolutions.add(stream.resolution)
            
            # Ordenar resoluções
            def resolution_sort_key(res):
                try:
                    return int(res.replace('p', ''))
                except:
                    return 0
            
            sorted_resolutions = sorted(all_resolutions, key=resolution_sort_key, reverse=True)
            self.available_resolutions = sorted_resolutions
            
            # Salvar streams para uso posterior
            self.video_streams = {
                'progressive': progressive_streams,
                'adaptive_video': adaptive_video_streams,
                'adaptive_audio': all_streams.filter(adaptive=True, only_audio=True),
                'audio_only': all_streams.filter(only_audio=True)
            }
            
            # Atualizar interface
            self.window.after(0, self._update_video_info)
            
        except VideoUnavailable:
            self.window.after(0, lambda: messagebox.showerror("Erro", "Vídeo indisponível ou removido!"))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Falha ao carregar vídeo: {str(e)}"))
        
        finally:
            self.window.after(0, lambda: self.get_info_button.configure(state="normal", text="🔍 Obter Informações"))
    
    def _update_video_info(self):
        try:
            # Informações básicas do vídeo
            title = self.yt.title[:100] + "..." if len(self.yt.title) > 100 else self.yt.title
            author = self.yt.author if self.yt.author else "Desconhecido"
            
            # Duração
            if self.yt.length:
                minutes = self.yt.length // 60
                seconds = self.yt.length % 60
                duration = f"{minutes}:{seconds:02d}"
            else:
                duration = "N/A"
            
            # Contar streams disponíveis
            total_streams = len(self.yt.streams)
            hd_streams = len(self.video_streams['adaptive_video'])
            
            # Informações detalhadas
            info_text = f"""
            🎬 Título: {title}
            👤 Canal: {author}
            ⏱️ Duração: {duration}
            
            📊 Streams disponíveis: {total_streams}
            🏆 Streams HD (1080p+): {hd_streams}
            
            🔍 Resoluções disponíveis:
            """
            
            # Adicionar resoluções disponíveis
            if self.available_resolutions:
                for res in self.available_resolutions[:8]:  # Mostrar até 8 resoluções
                    info_text += f"\n  • {res}"
                if len(self.available_resolutions) > 8:
                    info_text += f"\n  • ... e mais {len(self.available_resolutions) - 8} opções"
            else:
                info_text += "\n  Nenhuma resolução encontrada"
            
            self.info_label.configure(text=info_text)
            
            # Atualizar opções de resolução
            self.update_resolution_options()
            
            # Habilitar botão de download
            self.download_button.configure(state="normal")
            
            if hd_streams > 0:
                self.status_label.configure(text=f"✅ Vídeo carregado! {hd_streams} opções HD disponíveis.")
                self.download_button.configure(text="⬇️ Baixar em HD")
            else:
                self.status_label.configure(text="⚠️ Vídeo carregado, mas nenhuma opção HD encontrada.")
                self.download_button.configure(text="⬇️ Baixar")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar informações: {str(e)}")
            self.status_label.configure(text=f"Erro: {str(e)[:50]}...")
    
    def start_download(self):
        if self.downloading:
            return
            
        if not self.yt or not self.video_streams:
            messagebox.showerror("Erro", "Por favor, obtenha as informações do vídeo primeiro")
            return
        
        self.downloading = True
        self.cancel_download = False
        
        # Mostrar botão de cancelar
        self.cancel_button.pack(side="left", padx=5)
        self.cancel_button.configure(state="normal")
        
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        self.current_download_thread = thread
        thread.start()
    
    def cancel_download_process(self):
        self.cancel_download = True
        self.status_label.configure(text="Cancelando download...")
        self.cancel_button.configure(state="disabled")
    
    def download_video(self):
        try:
            self.window.after(0, lambda: self.download_button.configure(state="disabled", text="Processando..."))
            self.window.after(0, lambda: self.status_label.configure(text="Iniciando download..."))
            self.window.after(0, lambda: self.progress_bar.set(0))
            self.window.after(0, lambda: self.progress_label.configure(text="Progresso: 0%"))
            self.window.after(0, lambda: self.download_info_label.configure(text=""))
            
            download_path = self.download_path.get()
            
            # Criar pasta se não existir
            os.makedirs(download_path, exist_ok=True)
            
            download_type = self.download_type.get()
            selected_resolution = self.resolution_var.get()
            
            # Configurar callbacks no objeto YouTube
            self.yt.register_on_progress_callback(self.on_progress)
            self.yt.register_on_complete_callback(self.on_complete)
            
            if download_type == "audio":
                output_file = self._download_audio_only(download_path)
            elif download_type == "video_sd":
                output_file = self._download_sd_video(download_path, selected_resolution)
            else:  # video_hd
                output_file = self._download_hd_video(download_path, selected_resolution)
            
            if output_file and not self.cancel_download:
                self._show_success_message(download_path, os.path.basename(output_file))
            
        except Exception as e:
            if not self.cancel_download:
                self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro durante o download: {str(e)}"))
                self.window.after(0, lambda: self.status_label.configure(text=f"Erro: {str(e)[:50]}..."))
        
        finally:
            self.downloading = False
            self.window.after(0, lambda: self.download_button.configure(
                state="normal", 
                text="⬇️ Baixar em HD"
            ))
            self.window.after(0, lambda: self.cancel_button.configure(state="disabled"))
            self.window.after(0, lambda: self.cancel_button.pack_forget())
    
    def _download_audio_only(self, download_path):
        """Download apenas de áudio"""
        self.window.after(0, lambda: self.status_label.configure(text="Baixando áudio..."))
        
        # Pegar o melhor stream de áudio
        audio_stream = self.video_streams['audio_only'].get_audio_only()
        if not audio_stream:
            audio_stream = self.video_streams['audio_only'].first()
        
        if not audio_stream:
            raise Exception("Nenhum stream de áudio disponível")
        
        # Informações do stream
        self.window.after(0, lambda: self.download_info_label.configure(
            text=f"Áudio: {audio_stream.abr if hasattr(audio_stream, 'abr') else 'N/A'} | "
                 f"Tamanho estimado: {audio_stream.filesize_mb if hasattr(audio_stream, 'filesize_mb') else 'N/A'} MB"
        ))
        
        # Download
        output_file = audio_stream.download(output_path=download_path)
        
        # Renomear para .mp3
        base, ext = os.path.splitext(output_file)
        if ext.lower() != '.mp3':
            new_file = base + '.mp3'
            try:
                os.rename(output_file, new_file)
                return new_file
            except:
                return output_file
        
        return output_file
    
    def _download_sd_video(self, download_path, resolution):
        """Download de vídeo SD (progressive)"""
        self.window.after(0, lambda: self.status_label.configure(text=f"Baixando vídeo em {resolution}..."))
        
        # Encontrar stream progressivo na resolução desejada
        streams = self.video_streams['progressive']
        
        if resolution == "Melhor disponível":
            stream = streams.get_highest_resolution()
        else:
            stream = streams.filter(res=resolution).first()
            if not stream:
                stream = streams.get_highest_resolution()
                self.window.after(0, lambda: messagebox.showwarning(
                    "Aviso", 
                    f"Resolução {resolution} não disponível. Baixando {stream.resolution}."
                ))
        
        if not stream:
            raise Exception("Nenhum stream SD disponível")
        
        # Informações do stream
        self.window.after(0, lambda: self.download_info_label.configure(
            text=f"Vídeo: {stream.resolution} | "
                 f"Codec: {stream.codecs[0] if stream.codecs else 'N/A'} | "
                 f"Tamanho: {stream.filesize_mb if hasattr(stream, 'filesize_mb') else 'N/A'} MB"
        ))
        
        # Download
        return stream.download(output_path=download_path)
    
    def _download_hd_video(self, download_path, resolution):
        """Download de vídeo HD (pode ser combinado ou direto)"""
        # Primeiro, verificar se há streams progressivos em HD (raros, mas possíveis)
        progressive_hd = self.video_streams['progressive'].filter(res=resolution).first()
        
        if progressive_hd:
            # Se encontrar progressive em HD, usar ele (mais simples)
            self.window.after(0, lambda: self.status_label.configure(text=f"Baixando vídeo HD em {resolution}..."))
            
            self.window.after(0, lambda: self.download_info_label.configure(
                text=f"Vídeo HD: {progressive_hd.resolution} | "
                     f"Tamanho: {progressive_hd.filesize_mb if hasattr(progressive_hd, 'filesize_mb') else 'N/A'} MB"
            ))
            
            return progressive_hd.download(output_path=download_path)
        
        # Se não encontrar progressive HD, usar adaptive
        self.window.after(0, lambda: self.status_label.configure(
            text=f"Baixando vídeo HD ({resolution}) - Aguarde..."
        ))
        
        # Encontrar stream de vídeo adaptativo
        video_streams = self.video_streams['adaptive_video']
        
        if resolution == "Melhor disponível":
            video_stream = video_streams.get_highest_resolution()
        else:
            video_stream = video_streams.filter(res=resolution, mime_type="video/mp4").first()
            if not video_stream:
                # Tentar encontrar qualquer vídeo com essa resolução
                video_stream = video_streams.filter(res=resolution).first()
        
        if not video_stream:
            # Fallback para SD se não encontrar HD
            self.window.after(0, lambda: messagebox.showinfo(
                "Informação", 
                f"Resolução {resolution} não disponível como HD. Baixando a melhor qualidade SD disponível."
            ))
            return self._download_sd_video(download_path, "Melhor disponível")
        
        # Informações do stream
        self.window.after(0, lambda: self.download_info_label.configure(
            text=f"Vídeo HD: {video_stream.resolution} | "
                 f"FPS: {video_stream.fps if hasattr(video_stream, 'fps') else 'N/A'} | "
                 f"Codec: {video_stream.codecs[0] if video_stream.codecs else 'N/A'}"
        ))
        
        # Nome do arquivo baseado no título e resolução
        safe_title = "".join(c for c in self.yt.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title[:50]}_{resolution}.mp4"
        filepath = os.path.join(download_path, filename)
        
        # Download do vídeo HD
        return video_stream.download(output_path=download_path, filename=filename)
    
    def on_progress(self, stream, chunk, bytes_remaining):
        if self.cancel_download:
            raise Exception("Download cancelado pelo usuário")
            
        total_size = stream.filesize
        if total_size:
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            
            self.window.after(0, lambda: self.progress_bar.set(percentage / 100))
            self.window.after(0, lambda: self.progress_label.configure(text=f"Progresso: {percentage:.1f}%"))
            
            # Calcular velocidade e tempo restante
            current_time = time.time()
            if hasattr(self, 'last_update_time'):
                time_diff = current_time - self.last_update_time
                if time_diff > 0.5:  # Atualizar a cada 0.5 segundos
                    bytes_diff = bytes_downloaded - self.last_bytes_downloaded
                    speed_kbps = (bytes_diff / time_diff) / 1024
                    
                    if speed_kbps > 0:
                        bytes_left = bytes_remaining
                        time_left = bytes_left / (speed_kbps * 1024)
                        
                        if time_left < 60:
                            time_text = f"{time_left:.0f}s"
                        elif time_left < 3600:
                            time_text = f"{time_left/60:.1f}min"
                        else:
                            time_text = f"{time_left/3600:.1f}h"
                        
                        self.window.after(0, lambda: self.download_info_label.configure(
                            text=f"Velocidade: {speed_kbps:.0f} KB/s | Tempo restante: {time_text}"
                        ))
                    
                    self.last_update_time = current_time
                    self.last_bytes_downloaded = bytes_downloaded
            else:
                self.last_update_time = current_time
                self.last_bytes_downloaded = bytes_downloaded
    
    def on_complete(self, stream, file_path):
        self.window.after(0, lambda: self.progress_bar.set(1))
        self.window.after(0, lambda: self.progress_label.configure(text="Progresso: 100%"))
    
    def _show_success_message(self, folder_path, filename):
        """Mostrar mensagem de sucesso e opção para abrir pasta"""
        self.window.after(0, lambda: self.status_label.configure(
            text=f"✅ Download concluído: {filename}"
        ))
        
        # Perguntar se quer abrir a pasta
        self.window.after(1000, lambda: self.ask_open_folder(folder_path, filename))
    
    def ask_open_folder(self, folder_path, filename=None):
        message = "✅ Download concluído com sucesso!"
        if filename:
            message += f"\n\nArquivo: {filename}"
        
        result = messagebox.askyesno("Download Concluído", 
                                    f"{message}\n\nDeseja abrir a pasta de destino?")
        if result:
            try:
                os.startfile(folder_path)
            except:
                # Para Linux/Mac
                import subprocess
                try:
                    subprocess.Popen(['xdg-open', folder_path])
                except:
                    pass
    
    def run(self):
        self.window.mainloop()

def main():
    print("=" * 60)
    print("YouTube HD Downloader - Correção de Progresso")
    print("=" * 60)
    print("\nInstruções:")
    print("1. Cole a URL do vídeo do YouTube")
    print("2. Clique em 'Obter Informações'")
    print("3. Selecione 'Vídeo HD (1080p+)'")
    print("4. Escolha '1080p' ou 'Melhor disponível'")
    print("5. Clique em 'Baixar em HD'")
    print("\nNota: Alguns vídeos em 1080p+ podem não estar disponíveis")
    print("como streams progressivos. Nesse caso, será baixado")
    print("apenas o vídeo (sem áudio integrado).")
    print("=" * 60)
    
    app = YouTubeDownloaderApp()
    app.run()

if __name__ == "__main__":
    main()