#!/usr/bin/env python3
"""
简单的SSE流式接口压力测试脚本

用法:
    python scripts/simple_load_test.py --concurrent 10 --duration 60 --url https://chat.cmkjai.com/api/chat/stream_with_tts

功能:
    - 支持并发请求测试
    - 支持SSE流式响应处理
    - 实时显示测试进度和统计
    - 生成测试报告
"""

import argparse
import time
import threading
import requests
import json
import statistics
from datetime import datetime
from collections import defaultdict
from typing import List, Dict
import sys


class SSELoadTester:
    """SSE流式接口压力测试器"""
    
    def __init__(self, url: str, concurrent_users: int, duration_seconds: int, token: str):
        self.url = url
        self.concurrent_users = concurrent_users
        self.duration_seconds = duration_seconds
        self.token = token
        
        # 统计数据
        self.metrics = []
        self.errors = []
        self.lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.start_time = None
        
        # 测试数据
        self.test_messages = [
            "你好",
            "今天天气怎么样？",
            "请介绍一下糖尿病的预防方法",
            "血糖高了应该怎么办？",
            "运动对血糖有什么影响？",
        ]
    
    def _send_request(self, worker_id: int, user_id: int):
        """发送单个SSE请求"""
        request_id = f"worker_{worker_id}_{int(time.time() * 1000)}"
        conversation_id = f"chat_{user_id}_{int(time.time() * 1000)}"
        message = self.test_messages[worker_id % len(self.test_messages)]
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
        }
        
        payload = {
            'user_id': str(user_id),
            'message_content': message,
            'enable_tts': True,
            'conversation_id': conversation_id
        }
        
        start_time = time.time()
        first_byte_time = None
        first_content_time = None
        total_bytes = 0
        event_count = 0
        content_chunks = 0
        total_content_length = 0
        
        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            # 处理SSE流
            for line in response.iter_lines():
                if self.stop_flag.is_set():
                    break
                
                if first_byte_time is None:
                    first_byte_time = time.time()
                
                if line:
                    total_bytes += len(line)
                    line_str = line.decode('utf-8')
                    
                    # 解析SSE事件
                    if line_str.startswith('event:'):
                        event_count += 1
                    elif line_str.startswith('data:'):
                        try:
                            data_str = line_str[5:].strip()
                            if data_str:
                                data = json.loads(data_str)
                                # 检测首次内容到达
                                if first_content_time is None and data.get('content'):
                                    first_content_time = time.time()
                                # 统计内容块
                                if data.get('content'):
                                    content_chunks += 1
                                    total_content_length += len(data.get('content', ''))
                        except json.JSONDecodeError:
                            pass  # 忽略非JSON数据
            
            end_time = time.time()
            
            # 计算Token输出速度（字符/秒）
            total_time = end_time - start_time
            token_speed = total_content_length / total_time if total_time > 0 else 0
            
            # 记录成功的请求
            metric = {
                'request_id': request_id,
                'worker_id': worker_id,
                'start_time': start_time,
                'end_time': end_time,
                'response_time': end_time - start_time,
                'first_byte_time': first_byte_time - start_time if first_byte_time else None,
                'first_content_time': first_content_time - start_time if first_content_time else None,
                'status_code': response.status_code,
                'total_bytes': total_bytes,
                'event_count': event_count,
                'content_chunks': content_chunks,
                'total_content_length': total_content_length,
                'token_speed': token_speed,
                'is_success': True,
            }
            
            with self.lock:
                self.metrics.append(metric)
        
        except Exception as e:
            end_time = time.time()
            
            # 记录失败的请求
            error = {
                'request_id': request_id,
                'worker_id': worker_id,
                'start_time': start_time,
                'end_time': end_time,
                'response_time': end_time - start_time,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'is_success': False,
            }
            
            with self.lock:
                self.errors.append(error)
                self.metrics.append(error)
    
    def _worker_thread(self, worker_id: int):
        """工作线程 - 持续发送请求直到测试结束"""
        user_id = 13 + worker_id  # 使用不同的user_id
        
        while not self.stop_flag.is_set():
            elapsed = time.time() - self.start_time
            if elapsed >= self.duration_seconds:
                break
            
            self._send_request(worker_id, user_id)
            
            # 短暂休息，避免过于密集
            time.sleep(0.1)
    
    def _print_progress(self):
        """打印测试进度"""
        while not self.stop_flag.is_set():
            time.sleep(1)
            
            elapsed = time.time() - self.start_time
            if elapsed >= self.duration_seconds:
                break
            
            with self.lock:
                total_requests = len(self.metrics)
                successful_requests = sum(1 for m in self.metrics if m.get('is_success', False))
                failed_requests = len(self.errors)
                
                if total_requests > 0:
                    success_rate = (successful_requests / total_requests) * 100
                    avg_response_time = statistics.mean([m['response_time'] for m in self.metrics])
                    throughput = total_requests / elapsed
                else:
                    success_rate = 0
                    avg_response_time = 0
                    throughput = 0
            
            progress = (elapsed / self.duration_seconds) * 100
            
            sys.stdout.write(f"\r进度: {progress:.1f}% | "
                           f"请求数: {total_requests} | "
                           f"成功: {successful_requests} | "
                           f"失败: {failed_requests} | "
                           f"成功率: {success_rate:.1f}% | "
                           f"平均响应时间: {avg_response_time:.2f}s | "
                           f"吞吐量: {throughput:.2f} req/s")
            sys.stdout.flush()
    
    def run(self):
        """运行压力测试"""
        print(f"\n{'='*80}")
        print(f"开始压力测试")
        print(f"{'='*80}")
        print(f"目标URL: {self.url}")
        print(f"并发用户数: {self.concurrent_users}")
        print(f"测试持续时间: {self.duration_seconds}秒")
        print(f"{'='*80}\n")
        
        self.start_time = time.time()
        
        # 启动工作线程
        threads = []
        for i in range(self.concurrent_users):
            thread = threading.Thread(target=self._worker_thread, args=(i,))
            thread.start()
            threads.append(thread)
        
        # 启动进度显示线程
        progress_thread = threading.Thread(target=self._print_progress)
        progress_thread.start()
        
        # 等待测试完成
        try:
            time.sleep(self.duration_seconds)
        except KeyboardInterrupt:
            print("\n\n测试被用户中断")
        finally:
            self.stop_flag.set()
        
        # 等待所有线程结束
        for thread in threads:
            thread.join()
        progress_thread.join()
        
        print("\n\n测试完成，正在生成报告...\n")
        
        # 生成报告
        self._generate_report()
    
    def _generate_report(self):
        """生成测试报告"""
        total_requests = len(self.metrics)
        successful_requests = sum(1 for m in self.metrics if m.get('is_success', False))
        failed_requests = len(self.errors)
        
        if total_requests == 0:
            print("没有完成任何请求")
            return
        
        # 计算统计数据
        response_times = [m['response_time'] for m in self.metrics if m.get('is_success', False)]
        first_byte_times = [m['first_byte_time'] for m in self.metrics if m.get('is_success', False) and m.get('first_byte_time')]
        first_content_times = [m['first_content_time'] for m in self.metrics if m.get('is_success', False) and m.get('first_content_time')]
        token_speeds = [m['token_speed'] for m in self.metrics if m.get('is_success', False) and m.get('token_speed', 0) > 0]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # 计算百分位数
            sorted_times = sorted(response_times)
            p50 = sorted_times[int(len(sorted_times) * 0.50)]
            p90 = sorted_times[int(len(sorted_times) * 0.90)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response_time = 0
            min_response_time = 0
            max_response_time = 0
            p50 = p90 = p95 = p99 = 0
        
        # 首字节时间统计
        if first_byte_times:
            avg_first_byte = statistics.mean(first_byte_times)
            min_first_byte = min(first_byte_times)
            max_first_byte = max(first_byte_times)
        else:
            avg_first_byte = min_first_byte = max_first_byte = 0
        
        # 首次内容时间统计
        if first_content_times:
            avg_first_content = statistics.mean(first_content_times)
            min_first_content = min(first_content_times)
            max_first_content = max(first_content_times)
        else:
            avg_first_content = min_first_content = max_first_content = 0
        
        # Token速度统计
        if token_speeds:
            avg_token_speed = statistics.mean(token_speeds)
            min_token_speed = min(token_speeds)
            max_token_speed = max(token_speeds)
        else:
            avg_token_speed = min_token_speed = max_token_speed = 0
        
        success_rate = (successful_requests / total_requests) * 100
        error_rate = (failed_requests / total_requests) * 100
        packet_loss_rate = error_rate  # 对于HTTP请求，丢包率等同于错误率
        
        actual_duration = time.time() - self.start_time
        throughput = total_requests / actual_duration
        
        # 打印报告
        print(f"\n{'='*80}")
        print(f"压力测试报告")
        print(f"{'='*80}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"实际持续时间: {actual_duration:.2f}秒")
        print(f"\n【请求统计】")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求: {successful_requests}")
        print(f"  失败请求: {failed_requests}")
        print(f"  成功率: {success_rate:.2f}%")
        print(f"  错误率/丢包率: {error_rate:.2f}%")
        print(f"  吞吐量: {throughput:.2f} 请求/秒")
        
        if response_times:
            print(f"\n【响应时间统计】")
            print(f"  平均响应时间: {avg_response_time:.3f}秒")
            print(f"  最小响应时间: {min_response_time:.3f}秒")
            print(f"  最大响应时间: {max_response_time:.3f}秒")
            print(f"  P50 (中位数): {p50:.3f}秒")
            print(f"  P90: {p90:.3f}秒")
            print(f"  P95: {p95:.3f}秒")
            print(f"  P99: {p99:.3f}秒")
        
        if first_byte_times:
            print(f"\n【首字节响应时间 (TTFB)】")
            print(f"  平均首字节时间: {avg_first_byte:.3f}秒")
            print(f"  最小首字节时间: {min_first_byte:.3f}秒")
            print(f"  最大首字节时间: {max_first_byte:.3f}秒")
        
        if first_content_times:
            print(f"\n【首次内容响应时间】")
            print(f"  平均首次内容时间: {avg_first_content:.3f}秒")
            print(f"  最小首次内容时间: {min_first_content:.3f}秒")
            print(f"  最大首次内容时间: {max_first_content:.3f}秒")
        
        if token_speeds:
            print(f"\n【Token输出速度】")
            print(f"  平均输出速度: {avg_token_speed:.1f} 字符/秒")
            print(f"  最小输出速度: {min_token_speed:.1f} 字符/秒")
            print(f"  最大输出速度: {max_token_speed:.1f} 字符/秒")
        
        if self.errors:
            print(f"\n【错误统计】")
            error_types = defaultdict(int)
            for error in self.errors:
                error_types[error['error_type']] += 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}次")
        
        print(f"\n{'='*80}\n")
        
        # 保存详细数据到文件
        report_file = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'test_config': {
                'url': self.url,
                'concurrent_users': self.concurrent_users,
                'duration_seconds': self.duration_seconds,
            },
            'summary': {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'packet_loss_rate': packet_loss_rate,
                'throughput': throughput,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'p50': p50,
                'p90': p90,
                'p95': p95,
                'p99': p99,
                'avg_first_byte_time': avg_first_byte,
                'avg_first_content_time': avg_first_content,
                'avg_token_speed': avg_token_speed,
            },
            'metrics': self.metrics,
            'errors': self.errors,
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"详细报告已保存到: {report_file}")


def main():
    parser = argparse.ArgumentParser(description='SSE流式接口压力测试工具')
    parser.add_argument('--url', type=str, required=True, help='目标API URL')
    parser.add_argument('--concurrent', type=int, default=10, help='并发用户数 (默认: 10)')
    parser.add_argument('--duration', type=int, default=60, help='测试持续时间(秒) (默认: 60)')
    parser.add_argument('--token', type=str, required=True, help='认证Token')
    
    args = parser.parse_args()
    
    tester = SSELoadTester(
        url=args.url,
        concurrent_users=args.concurrent,
        duration_seconds=args.duration,
        token=args.token
    )
    
    tester.run()


if __name__ == '__main__':
    main()
