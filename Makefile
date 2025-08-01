# Generated by: Cursor (Claude)
# Makefile for MCP JIRA Server

.PHONY: help setup clean clean-cache test test-config test-server lint run-server test-mcp-server coverage coverage-html status default install-requirements-test install-cursor install-mcp
.DEFAULT_GOAL := default

# Variables
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
REQUIREMENTS = requirements.txt
REQUIREMENTS_TEST = requirements-test.txt

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m
PURPLE := \033[35m
WHITE := \033[37m
RESET := \033[0m

default: test coverage ## Run all tests and generate coverage report
	@printf "$(GREEN)Default target completed: tests and coverage generated!$(RESET)\n"

install-requirements-test: setup ## Install test requirements including coverage
	@printf "$(BLUE)Installing test dependencies...$(RESET)\n"
	@$(PIP) install -r $(REQUIREMENTS_TEST)
	@printf "$(GREEN)Test dependencies installed successfully!$(RESET)\n"

help: ## Show this help message
	@printf "$(WHITE)MCP JIRA Server - Available Commands$(RESET)\n"
	@printf "$(PURPLE)=======================================$(RESET)\n"
	@printf "\n"
	@awk 'BEGIN {FS = ":.*##"; printf "$(CYAN)Available Targets:$(RESET)\n"} \
		/^[a-zA-Z_][a-zA-Z0-9_-]*:.*##/ { \
			printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST)
	@printf "\n"
	@printf "$(YELLOW)Examples:$(RESET)\n"
	@printf "  make install-cursor        # Install MCP server for Cursor (recommended)\n"
	@printf "  make setup                 # Initial project setup\n"
	@printf "  make install-mcp           # Install MCP server package only\n"
	@printf "  make test                  # Run all tests with linting\n"
	@printf "  make coverage              # Run tests with coverage report\n"
	@printf "  make run-server            # Run MCP server (requires config)\n"
	@printf "  make test-mcp-server       # Test MCP server connectivity\n"
	@printf "\n"

setup: ## Setup - Create virtual environment and install dependencies
	@printf "$(BLUE)Setting up MCP JIRA Server...$(RESET)\n"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		printf "$(YELLOW)Creating virtual environment...$(RESET)\n"; \
		python3 -m venv $(VENV_DIR); \
	else \
		printf "$(GREEN)Virtual environment already exists$(RESET)\n"; \
	fi
	@printf "$(YELLOW)Installing dependencies...$(RESET)\n"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
	@printf "$(GREEN)Setup completed successfully!$(RESET)\n"
	@printf "\n"
	@printf "$(CYAN)Next steps:$(RESET)\n"
	@printf "  1. Create a configuration file (mcp_jira_server.yaml)\n"
	@printf "  2. Run 'make test' to verify installation\n"
	@printf "  3. Run 'make run-server' to start the MCP server\n"
	@printf "  4. See 'make help' for more options\n"

# Test targets
.PHONY: test test-config test-server test-all test-verbose test-no-lint

test: setup lint test-all  ## Run all unit tests with linting
	@printf "$(GREEN)All tests and linting completed successfully!$(RESET)\n"

test-config: setup  ## Run configuration module tests
	@printf "$(YELLOW)Running configuration tests...$(RESET)\n"
	$(PYTHON) -m unittest mcp_jira_server.test_config -v

test-server: setup  ## Run server module tests
	@printf "$(YELLOW)Running server tests...$(RESET)\n"
	$(PYTHON) -m unittest mcp_jira_server.test_server -v

test-all: setup  ## Run all tests (internal target)
	@printf "$(YELLOW)Running all unit tests...$(RESET)\n"
	$(PYTHON) -m unittest discover mcp_jira_server/ -v

test-verbose: setup lint  ## Run tests with maximum verbosity and linting
	@printf "$(YELLOW)Running all tests with detailed output...$(RESET)\n"
	$(PYTHON) -m unittest discover mcp_jira_server/ -v 2>&1 | cat

test-no-lint: setup test-all  ## Run all unit tests without linting
	@printf "$(GREEN)All tests completed successfully (no linting)!$(RESET)\n"

# MCP Server targets
.PHONY: run-server test-mcp-server

run-server: setup ## Run the MCP server (requires configuration file)
	@printf "$(BLUE)Starting MCP JIRA Server...$(RESET)\n"
	@if [ ! -f "mcp_jira_server.yaml" ] && [ -z "$(JIRA_URL)" ]; then \
		printf "$(RED)Error: Configuration required!$(RESET)\n"; \
		printf "$(YELLOW)Create 'mcp_jira_server.yaml' or set environment variables:$(RESET)\n"; \
		printf "  JIRA_URL=https://jira.company.com\n"; \
		printf "  JIRA_USER=username\n"; \
		printf "  JIRA_TOKEN=token\n"; \
		printf "$(CYAN)Example:$(RESET)\n"; \
		printf "  JIRA_URL=https://issues.redhat.com JIRA_USER=$$USER JIRA_TOKEN=mytoken make run-server\n"; \
		exit 1; \
	fi
	@if [ -n "$(JIRA_URL)" ]; then \
		printf "$(YELLOW)Using environment variables for configuration...$(RESET)\n"; \
		$(PYTHON) -m mcp_jira_server.server --url "$(JIRA_URL)" --username "$(JIRA_USER)" --token "$(JIRA_TOKEN)"; \
	else \
		printf "$(YELLOW)Using configuration file...$(RESET)\n"; \
		$(PYTHON) -m mcp_jira_server.server; \
	fi

test-mcp-server: setup ## Test MCP server functionality (requires JIRA_URL, JIRA_USER, JIRA_TOKEN)
	@printf "$(BLUE)Testing MCP server functionality...$(RESET)\n"
	@if [ -z "$(JIRA_URL)" ]; then \
		printf "$(RED)Error: JIRA_URL environment variable not set$(RESET)\n"; \
		printf "$(YELLOW)Usage: JIRA_URL=https://jira.company.com JIRA_USER=myuser JIRA_TOKEN=mytoken make test-mcp-server$(RESET)\n"; \
		exit 1; \
	fi
	@if [ -z "$(JIRA_USER)" ]; then \
		printf "$(RED)Error: JIRA_USER environment variable not set$(RESET)\n"; \
		exit 1; \
	fi
	@if [ -z "$(JIRA_TOKEN)" ]; then \
		printf "$(RED)Error: JIRA_TOKEN environment variable not set$(RESET)\n"; \
		exit 1; \
	fi
	@printf "$(YELLOW)Testing server startup and basic functionality...$(RESET)\n"
	@timeout 10s $(PYTHON) -m mcp_jira_server.server --url "$(JIRA_URL)" --username "$(JIRA_USER)" --token "$(JIRA_TOKEN)" || [ $$? -eq 124 ] && printf "$(GREEN)Server startup test completed$(RESET)\n"

# Coverage targets
.PHONY: coverage coverage-html

coverage: install-requirements-test ## Run tests with coverage and generate reports
	@printf "$(BLUE)Running tests with coverage...$(RESET)\n"
	@$(VENV_DIR)/bin/coverage run --source=mcp_jira_server --omit="mcp_jira_server/test_*.py" -m unittest discover mcp_jira_server/ -v
	@printf "$(YELLOW)Generating coverage report...$(RESET)\n"
	@$(VENV_DIR)/bin/coverage report -m
	@$(VENV_DIR)/bin/coverage xml
	@printf "$(GREEN)Coverage analysis completed!$(RESET)\n"

coverage-html: install-requirements-test ## Generate HTML coverage report
	@printf "$(BLUE)Running tests with coverage and generating HTML report...$(RESET)\n"
	@$(VENV_DIR)/bin/coverage run --source=mcp_jira_server --omit="mcp_jira_server/test_*.py" -m unittest discover mcp_jira_server/ -v
	@$(VENV_DIR)/bin/coverage html
	@printf "$(GREEN)HTML coverage report generated in htmlcov/ directory$(RESET)\n"
	@printf "$(CYAN)Open htmlcov/index.html in your browser to view the report$(RESET)\n"

lint: install-requirements-test ## Development - Run code linting
	@printf "$(BLUE)Running code linting...$(RESET)\n"
	@printf "$(CYAN)Linting MCP server files...$(RESET)\n"
	@$(VENV_DIR)/bin/flake8 mcp_jira_server/ --max-line-length=100 --ignore=E501,W503,W292 --exclude=mcp_jira_server/test_*.py
	@printf "$(CYAN)Linting test files...$(RESET)\n"
	@$(VENV_DIR)/bin/flake8 mcp_jira_server/test_*.py --max-line-length=120 --ignore=E501,W503,W291,W292,W293,E128

clean: clean-cache ## Maintenance - Remove virtual environment and cache files
	@printf "$(BLUE)Cleaning up MCP JIRA Server...$(RESET)\n"
	@printf "$(YELLOW)Removing virtual environment...$(RESET)\n"
	@rm -rf $(VENV_DIR)
	@printf "$(GREEN)Full cleanup completed!$(RESET)\n"

clean-cache: ## Maintenance - Remove only cache files (keep venv)
	@printf "$(BLUE)Cleaning Python cache files...$(RESET)\n"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@printf "$(BLUE)Cleaning coverage files...$(RESET)\n"
	@rm -rf htmlcov/ 2>/dev/null || true
	@rm -f .coverage coverage.xml 2>/dev/null || true
	@printf "$(GREEN)Cache cleanup completed!$(RESET)\n"

status: ## Show - Display current project status
	@printf "$(WHITE)MCP JIRA Server Project Status$(RESET)\n"
	@printf "$(PURPLE)===============================$(RESET)\n"
	@printf "\n"
	@printf "$(CYAN)Virtual Environment:$(RESET)\n"
	@if [ -d "$(VENV_DIR)" ]; then \
		printf "  $(GREEN)✓$(RESET) Virtual environment exists at $(VENV_DIR)\n"; \
		if [ -f "$(PYTHON)" ]; then \
			printf "  $(GREEN)✓$(RESET) Python executable found\n"; \
			$(PYTHON) --version | sed 's/^/  /'; \
		else \
			printf "  $(RED)✗$(RESET) Python executable not found\n"; \
		fi \
	else \
		printf "  $(RED)✗$(RESET) Virtual environment not found\n"; \
		printf "  $(YELLOW)→$(RESET) Run 'make setup' to create it\n"; \
	fi
	@printf "\n"
	@printf "$(CYAN)Dependencies:$(RESET)\n"
	@if [ -f "$(PYTHON)" ]; then \
		$(PYTHON) -c "import requests; print('  \\033[32m✓\\033[0m requests')" 2>/dev/null || printf "  $(RED)✗$(RESET) requests\n"; \
		$(PYTHON) -c "import yaml; print('  \\033[32m✓\\033[0m PyYAML')" 2>/dev/null || printf "  $(RED)✗$(RESET) PyYAML\n"; \
		$(PYTHON) -c "import mcp; print('  \\033[32m✓\\033[0m mcp')" 2>/dev/null || printf "  $(RED)✗$(RESET) mcp\n"; \
		$(PYTHON) -c "import pydantic; print('  \\033[32m✓\\033[0m pydantic')" 2>/dev/null || printf "  $(RED)✗$(RESET) pydantic\n"; \
	else \
		printf "  $(YELLOW)?$(RESET) Cannot check (no Python environment)\n"; \
	fi
	@printf "\n"
	@printf "$(CYAN)Project Files:$(RESET)\n"
	@for file in requirements.txt README.md; do \
		if [ -f "$$file" ]; then \
			printf "  $(GREEN)✓$(RESET) $$file\n"; \
		else \
			printf "  $(RED)✗$(RESET) $$file\n"; \
		fi \
	done
	@printf "$(CYAN)MCP Server Structure:$(RESET)\n"
	@for file in mcp_jira_server/__init__.py mcp_jira_server/server.py mcp_jira_server/config.py; do \
		if [ -f "$$file" ]; then \
			printf "  $(GREEN)✓$(RESET) $$file\n"; \
		else \
			printf "  $(RED)✗$(RESET) $$file\n"; \
		fi \
	done
	@printf "$(CYAN)JIRA Client:$(RESET)\n"
	@for file in jira_extractor/__init__.py jira_extractor/client.py; do \
		if [ -f "$$file" ]; then \
			printf "  $(GREEN)✓$(RESET) $$file\n"; \
		else \
			printf "  $(RED)✗$(RESET) $$file\n"; \
		fi \
	done
	@printf "$(CYAN)Test Files:$(RESET)\n"
	@for file in mcp_jira_server/test_config.py mcp_jira_server/test_server.py; do \
		if [ -f "$$file" ]; then \
			printf "  $(GREEN)✓$(RESET) $$file\n"; \
		else \
			printf "  $(RED)✗$(RESET) $$file\n"; \
		fi \
	done
	@printf "$(CYAN)Configuration:$(RESET)\n"
	@if [ -f "mcp_jira_server.yaml" ]; then \
		printf "  $(GREEN)✓$(RESET) mcp_jira_server.yaml (configuration file)\n"; \
	else \
		printf "  $(YELLOW)-$(RESET) mcp_jira_server.yaml (create for easier server startup)\n"; \
	fi
	@printf "$(CYAN)Coverage Files:$(RESET)\n"
	@if [ -f ".coverage" ]; then \
		printf "  $(GREEN)✓$(RESET) .coverage (coverage data)\n"; \
	else \
		printf "  $(YELLOW)-$(RESET) .coverage (run 'make coverage' to generate)\n"; \
	fi
	@if [ -f "coverage.xml" ]; then \
		printf "  $(GREEN)✓$(RESET) coverage.xml (XML report)\n"; \
	else \
		printf "  $(YELLOW)-$(RESET) coverage.xml (run 'make coverage' to generate)\n"; \
	fi
	@if [ -d "htmlcov" ]; then \
		printf "  $(GREEN)✓$(RESET) htmlcov/ (HTML report)\n"; \
	else \
		printf "  $(YELLOW)-$(RESET) htmlcov/ (run 'make coverage-html' to generate)\n"; \
	fi

# Installation targets
.PHONY: install-mcp install-cursor

install-mcp: setup ## Install the MCP JIRA server package
	@printf "$(BLUE)Installing MCP JIRA Server package...$(RESET)\n"
	@$(PIP) install -e .
	@printf "$(GREEN)MCP JIRA Server package installed successfully!$(RESET)\n"
	@printf "\n"
	@printf "$(CYAN)The server can now be run with:$(RESET)\n"
	@printf "  mcp-jira-server --config /path/to/config.yaml\n"
	@printf "  or\n"
	@printf "  python -m mcp_jira_server --config /path/to/config.yaml\n"

install-cursor: setup install-mcp ## Install MCP JIRA server for Cursor integration
	@printf "$(BLUE)Setting up MCP JIRA Server for Cursor...$(RESET)\n"
	@printf "$(YELLOW)Creating Cursor configuration...$(RESET)\n"
	@if [ ! -d "$$HOME/.cursor" ]; then \
		printf "$(RED)Error: Cursor directory ($$HOME/.cursor) not found!$(RESET)\n"; \
		printf "$(YELLOW)Please install Cursor first or create the directory manually$(RESET)\n"; \
		exit 1; \
	fi
	@if [ ! -f "$$HOME/.cursor/mcp_jira_server.yaml" ]; then \
		cp example_mcp_jira_server.yaml "$$HOME/.cursor/mcp_jira_server.yaml"; \
		printf "$(GREEN)Configuration file created: $$HOME/.cursor/mcp_jira_server.yaml$(RESET)\n"; \
	else \
		printf "$(YELLOW)Configuration file already exists: $$HOME/.cursor/mcp_jira_server.yaml$(RESET)\n"; \
		printf "$(CYAN)Keeping existing configuration (not overwritten)$(RESET)\n"; \
	fi
	@printf "$(YELLOW)Updating Cursor MCP configuration with venv Python...$(RESET)\n"
	@$(PYTHON) scripts/update_cursor_config.py "$$(pwd)/$(PYTHON)" "$$HOME/.cursor/mcp_jira_server.yaml" "$$(realpath .)"
	@printf "\n$(GREEN)Cursor MCP integration completed!$(RESET)\n"
	@printf "\n$(YELLOW)Next steps:$(RESET)\n"
	@printf "  1. Restart Cursor to load the new MCP server\n"
	@printf "  2. Open a new chat session (⌘+L on Mac, Ctrl+L on Linux)\n"
	@printf "  3. Look for 'jira' in the MCP servers sidebar\n"
	@printf "  4. Edit $$HOME/.cursor/mcp_jira_server.yaml to configure your JIRA instance\n" 