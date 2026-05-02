# Установка Docker Desktop на Windows 11 — Пошаговая инструкция

## Шаг 1: Установить WSL 2 (обязательно для Docker)

1. Нажмите **Пуск** → введите **PowerShell**
2. Правый клик → **Запуск от имени администратора**
3. Выполните:
   ```powershell
   wsl --install
   ```
4. **Перезагрузите компьютер**
5. После перезагрузки откроется окно Ubuntu — создайте логин и пароль

> Если Ubuntu не открылась автоматически: Пуск → Ubuntu

---

## Шаг 2: Скачать Docker Desktop

1. Откройте в браузере: https://www.docker.com/products/docker-desktop/
2. Нажмите **Download for Windows**
3. Запустите скачанный `Docker Desktop Installer.exe`

---

## Шаг 3: Установить Docker Desktop

При установке отметьте:
- ✅ **Use WSL 2 instead of Hyper-V** (обязательно!)
- ✅ **Add shortcut to desktop**

После установки — **перезагрузите компьютер**.

---

## Шаг 4: Запустить Docker Desktop

1. Пуск → **Docker Desktop**
2. Дождитесь, пока значок 🐋 в системном трее перестанет анимироваться (~1-2 мин)
3. При первом запуске можете пропустить регистрацию (Skip)

---

## Шаг 5: Проверить установку

Откройте **любой терминал** (CMD, PowerShell, VS Code) и выполните:
```cmd
docker --version
docker run hello-world
```

Должно вывести версию Docker и сообщение "Hello from Docker!".

---

## Шаг 6: Собрать и запустить Loadsheet App

В терминале из папки проекта `f:\loadsheet_app`:

```cmd
REM Сборка Docker-образа (первый раз ~3-5 мин)
docker build -t loadsheet-app .

REM Запуск контейнера
docker run -p 8080:8080 -e PORT=8080 -e CHECKWX_API_KEY=8dcbfc4fe37e443c8ea59b14d550f5c0 loadsheet-app
```

После запуска откройте в браузере: **http://localhost:8080**

---

## Полезные команды

```cmd
REM Список запущенных контейнеров
docker ps

REM Остановить контейнер
docker stop <CONTAINER_ID>

REM Логи контейнера
docker logs <CONTAINER_ID>

REM Удалить образ
docker rmi loadsheet-app

REM Пересобрать после изменений в коде
docker build -t loadsheet-app . --no-cache
```

---

## Возможные проблемы

### "WSL 2 installation is incomplete"
```powershell
wsl --update
wsl --set-default-version 2
```

### "Docker Desktop is not running"
Запустите Docker Desktop из меню Пуск и дождитесь полной загрузки.

### Ошибка сборки "no space left on device"
Docker Desktop → Settings → Resources → Disk image size → увеличить до 60 GB

### Порт 8080 занят
Замените порт: `docker run -p 9090:8080 -e PORT=8080 ...` и откройте http://localhost:9090
