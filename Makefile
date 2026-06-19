PYTHON ?= python
export PYTHONPATH := src

.PHONY: help install test demo clean

help:
	@echo "make test     # 运行 47 个单元测试（无需第三方库）"
	@echo "make demo     # 跑 examples/ 端到端演示（mine/locate/fix/analyze）"
	@echo "make install  # 安装可选 PDF 解码依赖（pymupdf/pdfplumber）"
	@echo "make clean    # 清理 __pycache__ 与生成文件"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

demo:
	@echo "===== mine =====";    $(PYTHON) -m hwtext mine examples/notices
	@echo "===== locate =====";  $(PYTHON) -m hwtext locate examples/textbook.txt --problems 3.2,9.9
	@echo "===== fix =====";     $(PYTHON) -m hwtext fix examples/answer.md -o examples/answer.fixed.md
	@echo "===== analyze ====="; $(PYTHON) -m hwtext analyze examples/answer.md

clean:
	rm -f examples/*.fixed.md
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
