import "./loader.scss";

interface LoaderProps {
  ligherBg?: boolean;
}

const Loader = ({ ligherBg }: LoaderProps) => {
  return (
    <div className={`loader-overlay${ligherBg ? " ligher-bg" : ""}`}>
      <div className="loader" />
    </div>
  );
};

export default Loader;
