# Design Document - Load Testing and Report Generation

## Overview

本设计文档描述了智糖小助手系统的压力测试和报告生成功能的技术实现方案。该功能将作为独立的服务模块集成到现有系统中，提供完整的压力测试能力，包括测试配置、执行、监控和报告生成。

核心设计目标：
- 支持对DeepSeek聊天API和Coze ASR API的并发压力测试
- 提供实时监控和详细的性能指标收集
- 生成可视化的HTML报告，支持多测试对比
- 评估系统稳定性，包括资源使用和性能衰减
- 提供RESTful API接口，支持CI/CD集成

技术栈选择：
- **压测引擎**: Locust（Python压测框架，支持分布式和实时监控）
- **数据存储**: MySQL（复用现有数据库）
- **报告生成**: Jinja2模板 + Chart.js（可视化图表）
- **异步任务**: Python asyncio + threading（并发请求处理）
- **API框架**: Flask Blueprint（与现有系统集成）

## Architecture

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Admin Frontend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Test Config  │  │ Real-time    │  │ Report View  │     │
│  │ Panel        │  │ Monitor      │  │ & Compare    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Load Testing Blueprint                     │  │
│  │  /api/load-test/config                              │  │
│  │  /api/load-test/start                               │  │
│  │  /api/load-test/status                              │  │
│  │  /api/load-test/stop                                │  │
│  │  /api/load-test/report                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Load Testing Service Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Test         │  │ Metrics      │  │ Report       │     │
│  │ Executor     │  │ Collector    │  │ Generator    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│   Target APIs           │  │   MySQL Database        │
│  ┌──────────────────┐   │  │  ┌──────────────────┐  │
│  │ DeepSeek Chat    │   │  │  │ load_test_runs   │  │
│  │ API              │   │  │  │ load_test_metrics│  │
│  └──────────────────┘   │  │  │ load_test_errors │  │
│  ┌──────────────────┐   │  │  └──────────────────┘  │
│  │ Coze ASR API     │   │  │                         │
│  └──────────────────┘   │  │                         │
└─────────────────────────┘  └─────────────────────────┘
```

### 数据流

1. **测试配置流程**:
   - 管理员通过前端配置测试参数
   - 后端验证配置并创建测试任务
   - 测试任务信息存储到数据库

2. **测试执行流程**:
   - Test Executor启动并发worker线程
   - 每个worker发送HTTP请求到目标API
   - Metrics Collector实时收集响应数据
   - 性能指标持久化到数据库

3. **监控流程**:
   - 前端通过WebSocket或轮询获取实时数据
   - 后端从内存和数据库读取最新指标
   - 实时更新图表和统计数据

4. **报告生成流程**:
   - Report Generator从数据库读取测试数据
   - 使用Jinja2模板渲染HTML报告
   - 集成Chart.js生成可视化图表
   - 返回报告URL供下载或预览

## Components and Interfaces

### 1. Load Testing Service (`services/load_testing_service.py`)

核心服务类，负责压力测试的整体协调。

```python
class LoadTestingService:
    """压力测试服务"""
    
    def create_test_run(self, config: Dict) -> int:
        """创建测试任务"""
        
    def start_test(self, test_run_id: int) -> bool:
        """启动压力测试"""
        
    def stop_test(self, test_run_id: int) -> bool:
        """停止压力测试"""
        
    def get_test_status(self, test_run_id: int) -> Dict:
        """获取测试状态"""
        
    def get_real_time_metrics(self, test_run_id: int) -> Dict:
        """获取实时指标"""
```

### 2. Test Executor (`services/test_executor.py`)

执行并发请求的核心组件。

```python
class TestExecutor:
    """测试执行器"""
    
    def __init__(self, config: Dict, metrics_collector: MetricsCollector):
        """初始化执行器"""
        
    def execute(self) -> None:
        """执行压力测试"""
        
    def _worker_thread(self, worker_id: int) -> None:
        """工作线程"""
        
    def _send_chat_request(self, user_id: int, message: str) -> Dict:
        """发送聊天请求"""
        
    def _send_asr_request(self, audio_data: bytes) -> Dict:
        """发送ASR请求"""
        
    def stop(self) -> None:
        """停止执行"""
```

### 3. Metrics Collector (`services/metrics_collector.py`)

收集和聚合性能指标。

```python
class MetricsCollector:
    """指标收集器"""
    
    def record_request(self, request_data: Dict) -> None:
        """记录单个请求"""
        
    def record_error(self, error_data: Dict) -> None:
        """记录错误"""
        
    def get_current_stats(self) -> Dict:
        """获取当前统计数据"""
        
    def calculate_percentiles(self) -> Dict:
        """计算响应时间百分位数"""
        
    def persist_metrics(self, test_run_id: int) -> None:
        """持久化指标到数据库"""
```

### 4. Report Generator (`services/report_generator.py`)

生成可视化报告。

```python
class ReportGenerator:
    """报告生成器"""
    
    def generate_html_report(self, test_run_id: int) -> str:
        """生成HTML报告"""
        
    def generate_comparison_report(self, test_run_ids: List[int]) -> str:
        """生成对比报告"""
        
    def _prepare_chart_data(self, metrics: List[Dict]) -> Dict:
        """准备图表数据"""
        
    def _calculate_performance_score(self, metrics: Dict) -> float:
        """计算性能评分"""
```

### 5. Load Testing Routes (`routes/load_testing.py`)

RESTful API端点。

```python
@load_test_bp.route('/config', methods=['POST'])
def create_test_config():
    """创建测试配置"""
    
@load_test_bp.route('/start', methods=['POST'])
def start_test():
    """启动压力测试"""
    
@load_test_bp.route('/status/<int:test_run_id>', methods=['GET'])
def get_test_status(test_run_id):
    """获取测试状态"""
    
@load_test_bp.route('/stop/<int:test_run_id>', methods=['POST'])
def stop_test(test_run_id):
    """停止测试"""
    
@load_test_bp.route('/report/<int:test_run_id>', methods=['GET'])
def get_report(test_run_id):
    """获取测试报告"""
    
@load_test_bp.route('/compare', methods=['POST'])
def compare_reports():
    """对比多个测试报告"""
```

## Data Models

### 数据库表设计

#### 1. load_test_runs（测试运行记录）

```sql
CREATE TABLE load_test_runs (
    test_run_id INT AUTO_INCREMENT PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    test_type ENUM('chat', 'asr', 'mixed') NOT NULL,
    config JSON NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed', 'stopped') DEFAULT 'pending',
    concurrent_users INT NOT NULL,
    duration_seconds INT NOT NULL,
    target_endpoint VARCHAR(500) NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    total_requests INT DEFAULT 0,
    successful_requests INT DEFAULT 0,
    failed_requests INT DEFAULT 0,
    avg_response_time FLOAT,
    min_response_time FLOAT,
    max_response_time FLOAT,
    p50_response_time FLOAT,
    p90_response_time FLOAT,
    p95_response_time FLOAT,
    p99_response_time FLOAT,
    throughput FLOAT,
    error_rate FLOAT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_test_type (test_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 2. load_test_metrics（详细指标记录）

```sql
CREATE TABLE load_test_metrics (
    metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_run_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    request_id VARCHAR(100),
    worker_id INT,
    request_type VARCHAR(50),
    response_time FLOAT NOT NULL,
    status_code INT,
    request_size INT,
    response_size INT,
    first_byte_time FLOAT,
    is_success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_run_id) REFERENCES load_test_runs(test_run_id) ON DELETE CASCADE,
    INDEX idx_test_run (test_run_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_is_success (is_success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 3. load_test_errors（错误记录）

```sql
CREATE TABLE load_test_errors (
    error_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_run_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_data JSON,
    occurrence_count INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_run_id) REFERENCES load_test_runs(test_run_id) ON DELETE CASCADE,
    INDEX idx_test_run (test_run_id),
    INDEX idx_error_type (error_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 4. load_test_system_metrics（系统资源指标）

```sql
CREATE TABLE load_test_system_metrics (
    system_metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_run_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    memory_available FLOAT,
    active_threads INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_run_id) REFERENCES load_test_runs(test_run_id) ON DELETE CASCADE,
    INDEX idx_test_run (test_run_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Python数据模型

```python
@dataclass
class TestConfig:
    """测试配置"""
    test_name: str
    test_type: str  # 'chat', 'asr', 'mixed'
    concurrent_users: int
    duration_seconds: int
    target_endpoint: str
    ramp_up_seconds: int = 0
    think_time_seconds: float = 0
    test_data: Dict = None

@dataclass
class RequestMetric:
    """请求指标"""
    request_id: str
    worker_id: int
    request_type: str
    start_time: float
    end_time: float
    response_time: float
    status_code: int
    is_success: bool
    error_message: str = None
    first_byte_time: float = None
    request_size: int = 0
    response_size: int = 0

@dataclass
class TestStats:
    """测试统计"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50: float
    p90: float
    p95: float
    p99: float
    throughput: float
    error_rate: float
    current_concurrent: int
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:
- Configuration validation properties (1.2, 8.1) can be combined into a single comprehensive validation property
- Request recording properties (2.4, 4.1) are redundant and can be merged
- Report content properties (5.2, 5.4) can be combined into a single report completeness property
- Statistical calculation properties (4.2, 4.3) can be unified into a single calculation correctness property

### Properties

Property 1: Configuration validation completeness
*For any* test configuration, validation should reject configurations with invalid concurrent user counts, invalid duration, or unreachable endpoints, and accept configurations with all valid parameters
**Validates: Requirements 1.2, 8.1**

Property 2: Task creation returns valid ID
*For any* valid test configuration, creating a test task should return a positive integer task ID
**Validates: Requirements 1.3**

Property 3: Test execution state transition
*For any* successfully created test task, starting the test should transition the status from "pending" to "running"
**Validates: Requirements 1.4**

Property 4: Status response completeness
*For any* test run, querying status should return a response containing progress percentage, completed request count, and estimated remaining time
**Validates: Requirements 1.5**

Property 5: Request data completeness
*For any* request sent during load testing, the recorded metric should contain timestamp, response time, status code, request size, and response size
**Validates: Requirements 2.4, 4.1**

Property 6: Error recording completeness
*For any* failed request, the error record should contain error type, error message, and timestamp
**Validates: Requirements 2.5**

Property 7: Statistics update frequency
*For any* running test, statistics should be updated at intervals not exceeding 1 second
**Validates: Requirements 3.1**

Property 8: Error threshold warning
*For any* test run, when the error rate exceeds the configured threshold, a warning flag should be set in the monitoring data
**Validates: Requirements 3.3**

Property 9: Graceful stop behavior
*For any* running test, calling stop should prevent new requests from being initiated and eventually transition status to "stopped"
**Validates: Requirements 3.5**

Property 10: Percentile calculation correctness
*For any* set of response times, the calculated P50, P90, P95, and P99 values should match the mathematical definition of percentiles
**Validates: Requirements 4.2**

Property 11: Statistical calculation correctness
*For any* completed test, the calculated average, minimum, maximum, and standard deviation of response times should be mathematically correct
**Validates: Requirements 4.3**

Property 12: Metrics persistence
*For any* completed test, all collected metrics should exist in the database after test completion
**Validates: Requirements 4.5**

Property 13: Report generation completeness
*For any* test run, the generated HTML report should contain test overview, configuration details, total requests, success rate, and average response time sections
**Validates: Requirements 5.2, 5.4**

Property 14: Report accessibility
*For any* generated report, both a download URL and preview URL should be available
**Validates: Requirements 5.5**

Property 15: Comparison calculation correctness
*For any* pair of test runs, the calculated performance difference percentage should equal ((new_value - old_value) / old_value) * 100
**Validates: Requirements 6.2**

Property 16: Resource monitoring during execution
*For any* running test, system resource metrics (CPU and memory usage) should be collected at regular intervals
**Validates: Requirements 7.1**

Property 17: Performance degradation detection
*For any* test running longer than 5 minutes, performance degradation analysis should be performed comparing early and late time segments
**Validates: Requirements 7.2**

Property 18: API response structure
*For any* valid API request to create a test, the response should contain task_id and status_url fields
**Validates: Requirements 8.2**

Property 19: Webhook notification on completion
*For any* test with a configured webhook URL, the webhook should be called with test results when the test completes
**Validates: Requirements 8.3**

Property 20: Status API JSON validity
*For any* status query via API, the response should be valid JSON containing progress and summary fields
**Validates: Requirements 8.4**

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Invalid parameter ranges (concurrent users < 1 or > 1000)
   - Invalid duration (< 1 second or > 24 hours)
   - Unreachable target endpoints
   - Missing required configuration fields

2. **Runtime Errors**
   - Network timeouts during test execution
   - API rate limiting responses (429 status codes)
   - Server errors from target APIs (5xx status codes)
   - Database connection failures
   - Memory exhaustion

3. **Data Errors**
   - Missing test data for execution
   - Corrupted audio files for ASR testing
   - Invalid user data from database
   - Malformed API responses

### Error Handling Strategies

1. **Validation Phase**
   - Validate all configuration parameters before creating test task
   - Return detailed error messages with specific validation failures
   - Check endpoint reachability before starting test

2. **Execution Phase**
   - Implement retry logic for transient network errors (max 3 retries)
   - Record all errors with full context (request data, stack trace)
   - Continue test execution even if individual requests fail
   - Implement circuit breaker for cascading failures (stop if error rate > 50%)

3. **Recovery Mechanisms**
   - Graceful degradation: reduce concurrent users if system overloaded
   - Automatic test pause on critical errors (database unavailable)
   - Save partial results if test is interrupted
   - Provide manual resume capability for paused tests

4. **Error Reporting**
   - Group similar errors to avoid log flooding
   - Include error distribution in test reports
   - Highlight critical errors that require immediate attention
   - Provide actionable recommendations for common errors

## Testing Strategy

### Unit Testing

**Test Coverage Areas:**
1. Configuration validation logic
2. Percentile calculation functions
3. Statistical calculation functions (mean, std dev, min, max)
4. Report data preparation and formatting
5. Error classification and grouping logic

**Testing Approach:**
- Use pytest framework for all unit tests
- Mock external dependencies (database, HTTP clients)
- Test edge cases (empty data sets, single data point, extreme values)
- Verify error handling for invalid inputs

### Property-Based Testing

**Property Testing Framework:** Hypothesis (Python property-based testing library)

**Configuration:**
- Minimum 100 iterations per property test
- Use custom generators for domain-specific data (test configs, metrics)
- Seed random generator for reproducibility

**Property Test Implementation:**
Each property-based test will be tagged with a comment referencing the design document property:

```python
# Feature: load-testing-report, Property 10: Percentile calculation correctness
@given(response_times=st.lists(st.floats(min_value=0.001, max_value=60.0), min_size=10))
def test_percentile_calculation_correctness(response_times):
    """Verify percentile calculations match mathematical definitions"""
    # Test implementation
```

**Key Property Tests:**
1. Property 1: Configuration validation - generate random configs, verify validation logic
2. Property 10: Percentile calculations - generate random response time lists, verify P50/P90/P95/P99
3. Property 11: Statistical calculations - verify mean, min, max, std dev correctness
4. Property 15: Comparison calculations - verify percentage difference formula
5. Property 5: Request data completeness - verify all required fields present in metrics

### Integration Testing

**Test Scenarios:**
1. End-to-end test execution flow (create → start → monitor → stop → report)
2. Database persistence and retrieval
3. Concurrent test execution (multiple tests running simultaneously)
4. Report generation with real test data
5. API endpoint integration

**Testing Approach:**
- Use test database with sample data
- Mock external API calls to DeepSeek/Coze
- Verify data consistency across components
- Test error scenarios (network failures, database errors)

### Performance Testing

**Self-Testing Capability:**
- Use the load testing system to test itself (meta-testing)
- Verify system can handle configured concurrent users
- Measure overhead of metrics collection
- Ensure report generation completes within acceptable time (< 5 seconds for 10K requests)
