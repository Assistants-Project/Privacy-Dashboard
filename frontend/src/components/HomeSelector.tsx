import { Button, Container } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { HomeModel } from "../../models/home";
import { Role, User } from "../../models/user";

function HomeSelector() {
    const auth = useAuth();
    const homes = auth.user?.homes ?? [];

    const renderOptional = (value: string | undefined) =>
        value && value.trim() ? value : <span className="muted">Non impostato</span>;

    const selectHome = (home: HomeModel) => {
        if (!auth.user) return;
        if (auth.user.current_home?.uuid === home.uuid) return;

        auth.setHome(
            new User(
                auth.user.email,
                auth.user.firstname,
                auth.user.lastname,
                auth.user.role,
                auth.user.homes,
            ),
            home
        );
    };

    return (
        <>
            <Container>
                <h2>Case</h2>
                <p className="muted">
                    Clicca su una casa per impostarla come casa corrente.
                </p>
                {homes.length ? (
                    <div className="d-flex flex-nowrap gap-3 overflow-auto pb-2">
                        {homes.map((home, idx) => {
                            const isSelected =
                                auth.user?.current_home?.uuid === home.uuid ||
                                (!auth.user?.current_home && idx === 0);

                            return (
                                <button
                                    key={home.uuid || idx}
                                    type="button"
                                    className={`card card-button ${isSelected ? "selected" : ""}`}
                                    style={{ minWidth: 280 }}
                                    onClick={() => selectHome(home)}
                                >
                                    <div style={{ fontWeight: 700 }}>
                                        {home.name?.trim()
                                            ? home.name
                                            : "Nome non impostato"}
                                    </div>
                                    <div className="muted" style={{ fontSize: 12 }}>
                                        UUID:{" "}
                                        {home.uuid?.trim() ? home.uuid : "Non impostato"}
                                    </div>
                                    <div className="kv-grid" style={{ marginTop: 12 }}>
                                        <div className="kv-row">
                                            <span>Address</span>
                                            <span>{renderOptional(home.address)}</span>
                                        </div>
                                        <div className="kv-row">
                                            <span>ZIP</span>
                                            <span>{renderOptional(home.zip_code)}</span>
                                        </div>
                                        <div className="kv-row">
                                            <span>Country</span>
                                            <span>{renderOptional(home.country)}</span>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                ) : (
                    <div className="card">
                        <div>Nessuna casa disponibile.</div>
                        <div className="muted">
                            La lista potrebbe essere vuota oppure non caricata.
                        </div>
                    </div>
                )}
            </Container>

        </>
    );
}

export { HomeSelector };
