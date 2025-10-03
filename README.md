# organizador-ia-windows
Aplicativo Windows para organizar arquivos locais com IA determinística e em nuvem.

## Build custom debian‑ia‑4g‑ptbr‑v1.iso

### ⚠️ Nota sobre erro de build (Debian wheezy – HTTP 404)

Durante a geração da ISO foram criados arquivos de log (`wget-log`, `wget‑log.1`, …) contendo a mensagem:

```
ERROR 404: Not Found – http://ftp.debian.org/debian/dists/wheezy/Release
```

#### Causa
* `wheezy` (Debian 7) foi movido para o **archive.debian.org**; os mirrors atuais não o servem mais.

#### Solução imediata
1. Substituir o mirror por `http://archive.debian.org/debian` nos arquivos de `sources.list` usados pelo live‑build.  
2. Desabilitar a verificação de validade dos arquivos *Release* (`Acquire::Check-Valid-Until "false"`).  
3. Executar `apt-get update` dentro do chroot.

Um script pronto para isso está em `scripts/fix-wheezy-archive.sh`. Basta rodá‑lo **dentro do chroot** (`sudo lb chroot && ./scripts/fix-wheezy-archive.sh`).

#### Solução a longo prazo
* Migrar a build para uma release suportada (ex.: `bookworm` ou `bullseye`). Isso elimina a necessidade de usar o archive e garante pacotes com atualizações de segurança.

--- (continua o restante do README) 

Como aplicar o patch no seu repositório
# 1️⃣ Baixe o diff (copie o conteúdo acima) para um arquivo temporário
cat > /tmp/patch.diff <<'EOF'
# <-- cole aqui todo o diff acima -->
EOF

# 2️⃣ No diretório raiz do seu projeto
git apply /tmp/patch.diff
git add scripts/fix-wheezy-archive.sh \
        config/includes.chroot/etc/apt/apt.conf.d/99no-check-valid-until \
        README.md
git commit -m "fix(build): use archive.debian.org for wheezy & disable Check-Valid-Until"

⚠️ Se preferir, pode simplesmente criar os arquivos manualmente com o conteúdo acima – o resultado será o mesmo.

🚀 Passo‑a‑passo para gerar a ISO final
Pré‑requisitos

Debian/Ubuntu host com
live-build

,
debootstrap

,
xorriso

,
wget

,
git

instalados.
Pelo menos 8 GB de espaço livre (para o chroot + ISO).
Conexão à internet (para baixar os pacotes do archive).
1️⃣ Preparar o ambiente
# Clone o repositório (se ainda não estiver local)
git clone https://github.com/gersonvida12-hash/organizador-ia-windows.git
cd organizador-ia-windows

# (Opcional) Crie um branch de trabalho
git checkout -b fix-wheezy-404

2️⃣ Aplicar o patch (caso ainda não tenha feito)
# Use o procedimento descrito acima ou copie os arquivos manualmente
git apply /tmp/patch.diff   # se já salvou o diff
git add .
git commit -m "apply wheezy‑archive fix"

3️⃣ Limpar o build anterior
sudo lb clean --all

4️⃣ Bootstrap (cria o chroot base)
sudo lb bootstrap --verbose 2>&1 | tee bootstrap.log

5️⃣ Entrar no chroot e aplicar a correção
sudo lb chroot
# Dentro do chroot:
./scripts/fix-wheezy-archive.sh
# Saia do chroot:
exit

O que acontece aqui?

O script faz backup de
sources.list

, aponta para
archive.debian.org

, desabilita a checagem de validade e executa
apt-get update

.
O arquivo
config/includes.chroot/etc/apt/apt.conf.d/99no-check-valid-until

garante que, em builds futuros, a configuração já esteja presente sem precisar rodar o script manualmente.
6️⃣ (Opcional) Ajustar preseed/autoinstall para ABNT2, login automático, sudo sem senha, particionamento total
Crie/edite
config/package-lists/auto-install.list.chroot

(exemplo mínimo):

# auto‑install.list.chroot
# teclado ABNT2
keyboard-configuration   keyboard-configuration/layoutcode=br
keyboard-configuration   keyboard-configuration/variantcode=abnt2

# login automático (systemd‑service)
systemd-sysv   systemd-sysv/enable=true
# sudo sem senha
sudo   sudoers.d/99_nopasswd   "solo ALL=(ALL) NOPASSWD: ALL"

Obs. Ajuste conforme a sua necessidade; o live‑build já inclui hooks para
preseed

/
autoinstall

.

7️⃣ Build da imagem binária (ISO)
sudo lb binary --verbose 2>&1 | tee binary.log

Se tudo correr bem, o arquivo
binary.hybrid.iso

aparecerá em
binary/

. Renomeie‑o:

mv binary/hybrid.iso debian-ia-4g-ptbr-v1.iso

8️⃣ Testar a ISO (opcional, mas recomendado)
# QEMU (rápido)
qemu-system-x86_64 -m 2048 -cdrom debian-ia-4g-ptbr-v1.iso -boot d

Verifique:

idioma/teclado PT‑BR, layout ABNT2
login automático como
solo

(senha vazia)
sudo

sem senha (
sudo -l

deve mostrar NOPASSWD)
desktop pgLX rodando em Wayland
chromium --enable-features=VaapiVideoDecoder

usa VA‑API (
glxinfo | grep "OpenGL renderer"

deve mostrar sua GPU integrada)
IA:
phi3

carregado via
trae.ai-system

(verifique processos ou UI do dashboard)
9️⃣ Criar pendrive bootável (Ventoy‑ready)
A ISO já está no formato hybrid (BIOS + UEFI). Basta copiar para o pendrive:

# Identifique o dispositivo (ex.: /dev/sdX)
sudo dd if=debian-ia-4g-ptbr-v1.iso of=/dev/sdX bs=4M status=progress oflag=sync
sync

⚠️
dd

sobrescreve todo o disco; confirme o dispositivo correto!
Se preferir usar Ventoy, basta colocar a ISO na partição do Ventoy – ele a detectará automaticamente.

📋 Checklist final (para garantir que a ISO está pronta)
✅	Item	Como validar
1	Repositorios apontando para archive.debian.org	
cat chroot/etc/apt/sources.list

→ contém
archive.debian.org

2	Check‑Valid‑Until desabilitado	
cat chroot/etc/apt/apt.conf.d/99no-check-valid-until

→
"false"

3	Login automático	Boot → usuário
solo

logado sem senha
4	Sudo sem senha	
sudo -n true

(não pede senha)
5	Particionamento total	Instalação limpa apaga todas as partições (verifique no instalador)
6	Desktop pgLX (Wayland)	
echo $XDG_SESSION_TYPE

→
wayland

7	Chromium VA‑API	
chromium --enable-features=VaapiVideoDecoder

→ reprodução de vídeo hardware‑accelerated
8	IA local	Dashboard
trae.ai-system

aparece ao iniciar sessão
9	Tema Ribon‑dark + Papirus + Plymouth animado	Tela de boot e login exibem os temas corretos
10	Boot híbrido	Teste em BIOS e UEFI (ou use Ventoy)
Se algum item falhar, abra o log correspondente (
binary.log

,
bootstrap.log

,
chroot.log

) e compartilhe as últimas linhas aqui para análise adicional.

📦 Resumo rápido (para copiar‑colar no agent)
# Aplicar patch
git apply /tmp/patch.diff
git add scripts/fix-wheezy-archive.sh \
        config/includes.chroot/etc/apt/apt.conf.d/99no-check-valid-until \
        README.md
git commit -m "fix(build): use archive.debian.org for wheezy & disable Check-Valid-Until"

# Build completo
sudo lb clean --all
sudo lb bootstrap
sudo lb chroot   # entra no chroot
./scripts/fix-wheezy-archive.sh
exit
sudo lb binary
mv binary/hybrid.iso debian-ia-4g-ptbr-v1.iso

Execute esses comandos no agent (ou no seu terminal) e, ao final, você terá a ISO pronta para gravar em pendrive e instalar em qualquer máquina com i3 / 4 GB RAM e vídeo integrado.
