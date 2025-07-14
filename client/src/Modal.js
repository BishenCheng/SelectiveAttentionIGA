import React from 'react';
import ReactDOM from 'react-dom';

const modalRoot = document.getElementById('modal-root');

class Modal extends React.Component {
  constructor(props) {
    super(props);
    this.el = document.createElement('div');
  }

  componentDidMount() {
    modalRoot.appendChild(this.el);
  }

  componentWillUnmount() {
    modalRoot.removeChild(this.el);
  }

  render() {
    const { 
      isOpen, 
      onClose, 
      currentImages, 
      currentPopulation, 
      selectedIndices,   
      historicalSelections, 
      setSelectedIndices,
      onDeleteHistoricalRecord,
      modalError, 
      onLogOperation 
    } = this.props;
    
    if (!isOpen) return null;

    const formatVaseCode = (vasecode) => {
      if (Array.isArray(vasecode)) {
        return vasecode.join(', ').substring(0, 30) + '...';
      }
      return typeof vasecode === 'string' ? `${vasecode.substring(0, 30)}...` : '在当前批次';
    };

    // 合并当前代和历史方案
    const allItems = [
      ...Array.from({length: currentPopulation.length}, (_, idx) => idx)
        .filter(index => selectedIndices.has(index))
        .map(index => ({
          ...currentPopulation[index],
          base64: currentImages.images[index],
          generation: currentImages.generation,
          index
        })),
      ...historicalSelections.flatMap(record => record.selections)
    ];

    return ReactDOM.createPortal(
      <div className="modal-overlay">
        <div className="modal-content">
          <button className="close-btn" onClick={onClose}>×</button>
          <h1>方案池</h1>
          {modalError && <p className="modal-error" style={{ color: 'red', margin: '10px 0' }}>{modalError}</p>} 
          <p>点击方案的右上角x图标可以删除该方案，点击右上角退出方案池</p>
          
          {/* 统一显示所有方案 */}
          <div className="all-modal-images">
            {allItems.map((item, index) => {
              if (!item) {
                console.warn(`Item at index ${index} is undefined`);
                return null;
              }
              return (
                <div key={`item-${index}`} className="modal-image-item">
                  <img 
                    src={item.base64} 
                    alt={`方案-${item.generation}-${item.index || index}`}
                    className="modal-image"
                  />
                  {/* 新增批次号显示 */}
                  <div className="generation-number">方案批次: {item.generation}</div>
                  <div className="vasecode">
                    {formatVaseCode(item.vasecode)}
                  </div>
                  <button 
                    className="delete-btn"
                    onClick={() => {
                      if (item.generation === currentImages.generation) {
                        const newSet = new Set(selectedIndices);
                        newSet.delete(item.index);
                        setSelectedIndices(newSet);
                      } else {
                        const genIndex = historicalSelections.findIndex(record => record.generation === item.generation);
                        const itemIndex = historicalSelections[genIndex].selections.findIndex(i => i.vasecode === item.vasecode);
                        onDeleteHistoricalRecord(genIndex, itemIndex);
                      }
                      onLogOperation(item.generation, item.vasecode, 'remove');
                    }}
                  >x</button>
                </div>
              );
            })}
          </div>
        </div>
      </div>,
      this.el
    );
  }
}

export default Modal;