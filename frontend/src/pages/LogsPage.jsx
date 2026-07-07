import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import { authStore } from "../store/authStore";

export default function LogsPage() {
  const navigate = useNavigate();
  const role = authStore((state) => state.role);
  const username = authStore((state) => state.username);
  const signOut = authStore((state) => state.signOut);

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadingFile, setDownloadingFile] = useState("");
  const [linkLoadingFile, setLinkLoadingFile] = useState("");
  const [presignedLinks, setPresignedLinks] = useState({});
  const [presignedMeta, setPresignedMeta] = useState({});
  const [copiedByFile, setCopiedByFile] = useState({});
  const [expiresSeconds, setExpiresSeconds] = useState(300);

  useEffect(() => {
    let active = true;

    const fetchLogs = async () => {
      try {
        setLoading(true);
        const response = await api.get("/logs");
        if (active) {
          setLogs(response.data);
          setError("");
        }
      } catch (err) {
        if (!active) return;

        if (err?.response?.status === 401) {
          signOut();
          navigate("/login", { replace: true });
          return;
        }

        setError("Nao foi possivel carregar os logs.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    fetchLogs();

    return () => {
      active = false;
    };
  }, [navigate, signOut]);

  const handleLogout = () => {
    signOut();
    navigate("/login", { replace: true });
  };

  const handleDownload = async (fileName) => {
    try {
      setDownloadingFile(fileName);
      const response = await api.get(`/logs/${encodeURIComponent(fileName)}`, {
        responseType: "blob",
      });

      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      if (err?.response?.status === 403) {
        setError("Seu perfil nao possui permissao para download.");
        return;
      }
      setError("Falha ao baixar arquivo.");
    } finally {
      setDownloadingFile("");
    }
  };

  const handlePresignedLink = async (fileName) => {
    try {
      setLinkLoadingFile(fileName);
      setError("");
      const response = await api.post(`/logs/${encodeURIComponent(fileName)}/presigned`, null, {
        params: { expires_seconds: expiresSeconds },
      });
      setPresignedLinks((current) => ({ ...current, [fileName]: response.data.url }));
      setPresignedMeta((current) => ({
        ...current,
        [fileName]: {
          expiresSeconds,
          generatedAt: Date.now(),
        },
      }));
      setCopiedByFile((current) => ({ ...current, [fileName]: false }));
    } catch (err) {
      if (err?.response?.status === 403) {
        setError("Seu perfil nao possui permissao para gerar link temporario.");
        return;
      }
      setError("Falha ao gerar link temporario.");
    } finally {
      setLinkLoadingFile("");
    }
  };

  const handleCopyLink = async (fileName) => {
    const url = presignedLinks[fileName];
    if (!url) {
      return;
    }

    try {
      await navigator.clipboard.writeText(url);
      setError("");
      setCopiedByFile((current) => ({ ...current, [fileName]: true }));
      setTimeout(() => {
        setCopiedByFile((current) => ({ ...current, [fileName]: false }));
      }, 1500);
    } catch {
      setError("Nao foi possivel copiar o link.");
    }
  };

  const formatExpiryLabel = (fileName) => {
    const meta = presignedMeta[fileName];
    if (!meta?.expiresSeconds) {
      return "";
    }
    const minutes = Math.round(meta.expiresSeconds / 60);
    return `Expira em ${minutes} min`;
  };

  return (
    <main className="page page-logs">
      <section className="atmosphere" aria-hidden="true" />
      <section className="panel reveal-delay">
        <header className="topbar">
          <div>
            <p className="kicker">Authenticated Area</p>
            <h1>Logs Bucket View</h1>
          </div>
          <div className="toolbar">
            <label className="expires-field">
              Expiracao
              <select
                value={expiresSeconds}
                onChange={(event) => setExpiresSeconds(Number(event.target.value))}
                disabled={role !== "admin"}
              >
                <option value={60}>1 min</option>
                <option value={300}>5 min</option>
                <option value={900}>15 min</option>
                <option value={3600}>60 min</option>
              </select>
            </label>
            <div className="identity">
              <span>{username || "usuario"}</span>
              <strong>{role || "viewer"}</strong>
              <button className="ghost" onClick={handleLogout}>
                Sair
              </button>
            </div>
          </div>
        </header>

        {error && <p className="error inline">{error}</p>}

        {loading ? (
          <p className="muted">Carregando arquivos...</p>
        ) : (
          <ul className="log-list">
            {logs.map((item) => (
              <li key={item.name}>
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.size} bytes</span>
                  {presignedLinks[item.name] && (
                    <div className="link-group">
                      <a
                        className="link-inline"
                        href={presignedLinks[item.name]}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Abrir link temporario
                      </a>
                      <button className="ghost tiny" onClick={() => handleCopyLink(item.name)}>
                        Copiar link
                      </button>
                      <span className="link-meta">{formatExpiryLabel(item.name)}</span>
                      {copiedByFile[item.name] && <span className="copied-state">Copiado</span>}
                    </div>
                  )}
                </div>
                <div className="actions">
                  <button
                    onClick={() => handleDownload(item.name)}
                    disabled={role !== "admin" || downloadingFile === item.name}
                  >
                    {downloadingFile === item.name ? "Baixando..." : "Download"}
                  </button>
                  <button
                    className="ghost"
                    onClick={() => handlePresignedLink(item.name)}
                    disabled={role !== "admin" || linkLoadingFile === item.name}
                  >
                    {linkLoadingFile === item.name ? "Gerando..." : "Link temporario"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {role !== "admin" && (
          <p className="muted">Perfil viewer: voce pode listar os logs, mas nao baixar.</p>
        )}
      </section>
    </main>
  );
}
