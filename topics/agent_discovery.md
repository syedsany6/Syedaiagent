# Discovering Agent (Card)s

<!-- TOC -->

- [Discovering Agent Cards](#discovering-agent-cards)
  - [Open Discovery](#open-discovery)
  - [Curated Discovery (Registry-Based)](#curated-discovery-registry-based)
  - [Private Discovery (API-Based)](#private-discovery-api-based)
  - [Securing Agent Cards](#securing-agent-cards)

<!-- /TOC -->

A2A's [AgentCard](/documentation.md#agent-card) standardizes the *format* of the data shared during discovery. However there are unlimited ways to discover these agent cards. We anticipate this being an open topic for discussion and look forward to ideas from the community.

Here is our current thinking. 

## Open Discovery
We recommend enterprises host their agent cards at a well-known path. Specifically: https://`DOMAIN`/.well-known/agent.json. Clients will use DNS to resolve a known or found domain, send a simple `GET` request to the path, and receive the agent card. 

This will enable web-crawlers and applications to easily discover agents for known or configured domains. This effectively reduces the discovery process to "find a domain". 

## Curated Discovery (Registry-Based)
We anticipate enterprise applications making curated registries of agents available through a catalog interface. This opens up more enterprise scenarios such as organization-specific agent registries that are curated by an administrator. 


我们提议设计一个在组织范围内全局唯一的 Agent Registrar，用来提供 Registry-Based 的 Agent 服务发现能力。
组织由多个团队组成，每个团队可以管理自己拥有的 Agent，而每个 Agent 必须属于唯一的一个团体。
Agent Registrar 包括以下必须的能力：
- Team Management：负责团队的注册、更新、删除，例如能够回答 "创建一个新团队"。
- Agent Registry：负责 Agent 的注册，反注册和更新注册信息，例如能够回答 "注册我的代理，其具备以下功能：..."
- Agent Discovery：基于各种标准和能力发现已经注册的合适的 Agent，例如能够回答 "寻找能够处理 pfd 文档的 agent"。

![](../images/discovery/a2a_organization_team.png)

Agent Registrar 也可以提供一些可选的能力：
- Registry Analytics：提供关于已注册的 Agent 的分析和见解，例如能够回答 "哪个 agent 的评分最高？" 。

### Team Management

团队需要在 Agent Registrar 中注册，Agent Registrar 会为每个团队分配唯一的 `teamID`。

###  Agent Registry 

#### Agent 的可见性
Agent 的可见性是指该 Agent 是否可以被团队内或团队外其他 Agent 发现， Agent 注册到 Agent Registrar 的方式会影响其可见性。

Agent 可以选择 private 或者 public 的方式注册到 Agent Registrar 中，默认采用 public 的方式注册。

| Agent 的注册方式 | 是否可以被团队内的其他 Agent 发现 | 是否可以被团队外的 Agent 发现 |
|-------------|----------------------|--------------------|
| private     | Yes                  | No                 |
| public      | Yes                  | Yes                |

Agent 通过明确指指定 `teamID` 和 `visibility` 字段来控制 Agent 的可见性。
在 Agent Registrar 的所有交互都需要带上 `teamID` 字段用来标志 Agent 所属的 Team, 每个 Agent 的 `teamID` 有且只有一个。

在使用 Agent Registrar 进行 Agent 注册和更新时, 使用 `visibility` 字段，其有两个可选值：
- `private`: 只对同团队内的其他 Agent 可见
- `public`: 对团队内和团队外的 Agent 都可见

### 鉴权与认证

Agent 往 Agent Registrar 注册时，需要持有团队分发的  `teamToken` 对 Agent 进行鉴权。 


### Agent Registrar 的 Agent 实现

Agent Registrar 可以使用 Agent 来实现， 其 Agent Card 可以描述为：

```json
{
  "name": "Agent Registrar ",
  "description": "A specialized agent that provides registry-based discovery services for A2A agents. It maintains a catalog of registered agents and helps clients find the most suitable agents for their tasks based on capabilities and requirements.",
  "url": "https://discovery-agent.google.com",
  "provider": {
    "organization": "Google",
    "url": https://google.com"
  },
  "version": "1.0.0",
  "documentationUrl": "https://discovery-agent.google.com/docs",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["OAuth2"]
  },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["application/json", "text/html"],
  "skills": [
    {
      "id": "team-management",
      "name": "Team Management",
      "description": "Manages teams within the organization with CRUD operations for team administration",
      "tags": ["team", "management", "administration", "organization"],
      "examples": [
        "Create a new team for my organization",
        "Update our team information",
        "Delete our existing team",
        "List all teams in our organization",
        "Retrieve our team's details and token"
      ],
      "inputModes": ["application/json", "text/plain"],
      "outputModes": ["application/json"]
    },
    {
      "id": "agent-registry",
      "name": "Agent Registry",
      "description": "Manages the registry of A2A agents with CRUD operations for agent registration",
      "tags": ["registry", "management", "administration"],
      "examples": [
        "Register my agent with the following capabilities...",
        "Update my agent's information",
        "Remove my agent from the registry"
      ],
      "inputModes": ["application/json"],
      "outputModes": ["application/json"]
    },
    {
      "id": "agent-discovery",
      "name": "Agent Discovery",
      "description": "Discovers agents that match specific criteria or capabilities",
      "tags": ["discovery", "search", "find"],
      "examples": [
        "Find agents that can process PDF documents",
        "Which agents support video analysis?",
        "Find an agent that can translate from Chinese to English",
        "List all available financial reporting agents"
      ],
      "inputModes": ["text/plain", "application/json"],
      "outputModes": ["application/json"]
    },
    {
      "id": "registry-analytics",
      "name": "Registry Analytics",
      "description": "Provides analytics and insights about registered agents",
      "tags": ["analytics", "statistics", "reporting"],
      "examples": [
        "What are the most popular agent categories?",
        "Generate a report of agent usage statistics",
        "Which agents have the highest rating?"
      ],
      "inputModes": ["text/plain"],
      "outputModes": ["application/json", "text/html"]
    },
  ]
}
```

#### 其他 Agent 和 Agent Registrar 的交互流程

下面通过 SendTask 来展示其他 Agent 和 Agent Registrar 的交互流程：

```json
// 1. Team Registration Request
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tasks/send",
  "params": {
    "id": "team-reg-task-123456",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "创建一个新团队"
        },
        {
          "type": "data",
          "data": {
            "operation": "registerTeam",
            "adminToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "teamInfo": {
              "name": "FinTech Solutions Team",
              "description": "Financial technology solutions development team",
              "contact": "team-lead@fintechsolutions.example.com"
            }
          }
        }
      ]
    }
  }
}

// 2. Agent Registrar Response (Team Registration Success)
// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "team-reg-task-123456",
    "sessionId": "session-789012",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T13:25:17.328Z"
    },
    "artifacts": [
      {
        "name": "team-registration-result",
        "parts": [
          {
            "type": "data",
            "data": {
              "registrationStatus": "success",
              "teamID": "team-fintech-123",
              "teamToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
              "registrationTimestamp": "2023-09-15T13:25:16.912Z",
              "message": "Your team has been successfully registered with the A2A Registry."
            }
          },
          {
            "type": "text",
            "text": "Your team 'FinTech Solutions Team' has been successfully registered. Your Team ID is: team-fintech-123. Please securely store your teamToken as it will be required for all team operations and agent registrations."
          }
        ]
      }
    ]
  }
}

// 3. Team Update Request
// Request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tasks/send",
  "params": {
    "id": "team-update-task-234567",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "更新我的团队信息"
        },
        {
          "type": "data",
          "data": {
            "operation": "updateTeam",
            "teamID": "team-fintech-123",
            "teamToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "updates": {
              "name": "FinTech Enterprise Solutions",
              "description": "Enterprise financial technology solutions and consulting team",
              "contact": "enterprise-lead@fintechsolutions.example.com"
            }
          }
        }
      ]
    }
  }
}

// 4. Agent Registrar Response (Team Update Success)
// Response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "id": "team-update-task-234567",
    "sessionId": "session-345678",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T14:12:08.541Z"
    },
    "artifacts": [
      {
        "name": "team-update-result",
        "parts": [
          {
            "type": "data",
            "data": {
              "updateStatus": "success",
              "teamID": "team-fintech-123",
              "updateTimestamp": "2023-09-15T14:12:07.823Z",
              "message": "Your team information has been successfully updated."
            }
          },
          {
            "type": "text",
            "text": "Your team information has been successfully updated. Team name changed to 'FinTech Enterprise Solutions'."
          }
        ]
      }
    ]
  }
}

// 5. Agent Registration Request (with Team Authentication)
// Request
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tasks/send",
  "params": {
    "id": "reg-task-123456",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Register my agent"
        },
        {
          "type": "data",
          "data": {
            "operation": "register",
            "teamID": "team-fintech-123",
            "teamToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "visibility": "private",
            "agentCard": {
              "name": "Finance Reports Agent",
              "description": "An agent specialized in generating financial reports and analysis",
              "url": "https://finance-agent.example.com",
              "provider": {
                "organization": "FinTech Solutions",
                "url": "https://fintechsolutions.example.com"
              },
              "version": "1.0.0",
              "capabilities": {
                "streaming": true,
                "pushNotifications": false
              },
              "authentication": {
                "schemes": ["OAuth2", "ApiKey"]
              },
              "defaultInputModes": ["text/plain", "application/json"],
              "defaultOutputModes": ["text/plain", "application/json", "application/pdf"],
              "skills": [
                {
                  "id": "financial-analysis",
                  "name": "Financial Analysis",
                  "description": "Analyzes financial data and generates insights",
                  "tags": ["finance", "analysis", "reporting"],
                  "examples": [
                    "Generate a quarterly financial report",
                    "Analyze our cash flow trends"
                  ]
                },
                {
                  "id": "budget-forecasting",
                  "name": "Budget Forecasting",
                  "description": "Creates budget forecasts based on historical data",
                  "tags": ["budget", "forecast", "planning"],
                  "examples": [
                    "Create a budget forecast for next year",
                    "Predict our expenses for Q3"
                  ]
                }
              ]
            },
            "metadata": {
              "tags": ["finance", "enterprise", "reporting"],
              "category": "business",
              "subCategory": "finance"
            }
          }
        }
      ]
    }
  }
}

// 6. Agent Registrar Response (Success - Team Authentication)
// Response
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "id": "reg-task-123456",
    "sessionId": "session-789012",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T14:28:32.415Z"
    },
    "artifacts": [
      {
        "name": "registration-result",
        "parts": [
          {
            "type": "data",
            "data": {
              "registrationStatus": "success",
              "registryId": "agent-fin-345678",
              "teamID": "team-fintech-123",
              "registrationTimestamp": "2023-09-15T14:28:31.982Z",
              "visibility": "private",
              "message": "Your agent has been successfully registered with the A2A Registry."
            }
          },
          {
            "type": "text",
            "text": "Your Finance Reports Agent has been successfully registered with the A2A Registry. Registry ID: agent-fin-345678."
          }
        ]
      }
    ]
  }
}

// 7. Registration Request (Failed - No Team Authentication)
// Request
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tasks/send",
  "params": {
    "id": "failed-reg-task-234567",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Register my agent"
        },
        {
          "type": "data",
          "data": {
            "operation": "register",
            "agentCard": {
              "name": "Data Analysis Agent",
              "description": "An agent for data analysis and visualization",
              "url": "https://data-agent.example.com",
              "provider": {
                "organization": "Data Insights LLC",
                "url": "https://datainsights.example.com"
              },
              "version": "1.0.0"
              // Rest of agent card...
            }
          }
        }
      ]
    }
  }
}

// 8. Agent Registrar Response (Failed - Team Authentication Required)
// Response
{
  "jsonrpc": "2.0",
  "id": 4,
  "error": {
    "code": -32401,
    "message": "Team authentication required",
    "data": {
      "operation": "register",
      "requiredFields": ["teamID", "teamToken"],
      "authenticationEndpoint": "https://agent-registrar.example.com/auth"
    }
  }
}

// 9. Update Agent Information (with Team Authentication)
// Request
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tasks/send",
  "params": {
    "id": "update-task-345678",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Update my agent information"
        },
        {
          "type": "data",
          "data": {
            "operation": "update",
            "registryId": "agent-fin-345678",
            "teamID": "team-fintech-123",
            "teamToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "updates": {
              "agentCard": {
                "version": "1.1.0",
                "description": "A comprehensive agent specialized in generating financial reports, analysis and investment recommendations",
                "skills": [
                  {
                    "id": "investment-advisor",
                    "name": "Investment Advisor",
                    "description": "Provides investment recommendations based on financial data",
                    "tags": ["investment", "advisor", "recommendations"],
                    "examples": [
                      "Recommend investment strategies for my portfolio",
                      "Analyze market trends and suggest investments"
                    ]
                  }
                ]
              },
              "visibility": "public",
              "metadata": {
                "tags": ["finance", "enterprise", "reporting", "investment"]
              }
            }
          }
        }
      ]
    }
  }
}

// 10. Agent Registrar Update Response (Success - Team Authentication)
// Response
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "id": "update-task-345678",
    "sessionId": "session-456789",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T15:36:45.712Z"
    },
    "artifacts": [
      {
        "name": "update-result",
        "parts": [
          {
            "type": "data",
            "data": {
              "updateStatus": "success",
              "registryId": "agent-fin-345678",
              "teamID": "team-fintech-123",
              "updateTimestamp": "2023-09-15T15:36:44.521Z",
              "visibility": "public",
              "message": "Your agent information has been successfully updated."
            }
          },
          {
            "type": "text",
            "text": "Your Finance Reports Agent (ID: agent-fin-345678) information has been successfully updated. Version updated to 1.1.0 and added new skill 'Investment Advisor'."
          }
        ]
      }
    ]
  }
}

// 11. Agent Discovery Request (No Team Authentication Required for Public Agents)
// Request
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tasks/send",
  "params": {
    "id": "discovery-task-456789",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Find agents that can process PDF documents"
        }
      ]
    }
  }
}

// 12. Agent Registrar Response (Discovery operations of public agents don't require auth)
// Response
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "id": "discovery-task-456789",
    "sessionId": "session-567890",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T16:12:22.891Z"
    },
    "artifacts": [
      {
        "name": "discovery-results",
        "parts": [
          {
            "type": "data",
            "data": {
              "matches": [
                {
                  "registryId": "agent-doc-123456",
                  "agentCard": {
                    "name": "Document Processing Agent",
                    "description": "An agent specialized in processing and analyzing various document formats",
                    "url": "https://doc-agent.example.com",
                    "provider": {
                      "organization": "DocTech Solutions",
                      "url": "https://doctech.example.com"
                    },
                    "version": "2.0.0",
                    "capabilities": {
                      "streaming": true,
                      "pushNotifications": true
                    },
                    "defaultInputModes": ["application/pdf", "image/jpeg", "image/png", "text/plain"],
                    "defaultOutputModes": ["text/plain", "application/json", "application/pdf"]
                  },
                  "teamID": "team-doctech-456",
                  "visibility": "public",
                  "matchScore": 0.95,
                  "matchReason": "Explicit support for PDF processing in input modes"
                },
                // Second result omitted for brevity
              ],
              "totalMatches": 2,
              "searchCriteria": {
                "capability": "PDF processing"
              }
            }
          },
          {
            "type": "text",
            "text": "I found 2 agents that can process PDF documents:\n\n1. Document Processing Agent (DocTech Solutions) - An agent specialized in processing and analyzing various document formats, with full PDF input support\n\n2. Content Analysis AI (AI Research Group) - AI agent for analyzing and extracting information from various content types, including PDF documents"
          }
        ]
      }
    ]
  }
}

// 13. Team-specific Agent Discovery Request (Authenticated - includes private team agents)
// Request
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tasks/send",
  "params": {
    "id": "team-discovery-task-567890",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Find all finance agents in my team"
        },
        {
          "type": "data",
          "data": {
            "operation": "discover",
            "teamID": "team-fintech-123",
            "teamToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "searchCriteria": {
              "capability": "finance",
              "includePrivate": true
            }
          }
        }
      ]
    }
  }
}

// 14. Agent Registrar Team Discovery Response
// Response
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "id": "team-discovery-task-567890",
    "sessionId": "session-678901",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T16:28:53.476Z"
    },
    "artifacts": [
      {
        "name": "discovery-results",
        "parts": [
          {
            "type": "data",
            "data": {
              "matches": [
                {
                  "registryId": "agent-fin-345678",
                  "agentCard": {
                    "name": "Finance Reports Agent",
                    "description": "A comprehensive agent specialized in generating financial reports, analysis and investment recommendations",
                    // Agent card details omitted for brevity
                  },
                  "teamID": "team-fintech-123",
                  "visibility": "public",
                  "matchScore": 0.98,
                  "matchReason": "Direct match for finance capabilities"
                },
                {
                  "registryId": "agent-fin-567890",
                  "agentCard": {
                    "name": "Budget Planning Agent",
                    "description": "Private team agent for internal budget planning and forecasting",
                    // Agent card details omitted for brevity
                  },
                  "teamID": "team-fintech-123",
                  "visibility": "private",
                  "matchScore": 0.92,
                  "matchReason": "Team-only agent with finance capabilities"
                }
              ],
              "totalMatches": 2,
              "searchCriteria": {
                "capability": "finance",
                "teamID": "team-fintech-123",
                "includePrivate": true
              }
            }
          },
          {
            "type": "text",
            "text": "I found 2 finance agents in your team:\n\n1. Finance Reports Agent - A comprehensive agent for financial reports and investment recommendations (public)\n\n2. Budget Planning Agent - Internal team agent for budget planning and forecasting (private)"
          }
        ]
      }
    ]
  }
}

// 15. Agent Deregistration Request (with Team Authentication)
// Request
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tasks/send",
  "params": {
    "id": "deregister-task-678901",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Remove my agent from the registry"
        },
        {
          "type": "data",
          "data": {
            "operation": "deregister",
            "registryId": "agent-fin-345678",
            "teamID": "team-fintech-123",
            "teamToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
          }
        }
      ]
    }
  }
}

// 16. Agent Registrar Deregistration Response (Success - Team Authenticated)
// Response
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "id": "deregister-task-678901",
    "sessionId": "session-789012",
    "status": {
      "state": "completed",
      "timestamp": "2023-09-15T17:05:18.913Z"
    },
    "artifacts": [
      {
        "name": "deregistration-result",
        "parts": [
          {
            "type": "data",
            "data": {
              "deregistrationStatus": "success",
              "registryId": "agent-fin-345678",
              "teamID": "team-fintech-123",
              "deregistrationTimestamp": "2023-09-15T17:05:17.842Z",
              "message": "Your agent has been successfully removed from the registry."
            }
          },
          {
            "type": "text",
            "text": "Your Finance Reports Agent (ID: agent-fin-345678) has been successfully removed from the A2A Registry."
          }
        ]
      }
    ]
  }
}
```

*We **are** considering adding Registry support to the protocol - please drop us a [note](https://github.com/google/A2A/blob/main/README.md#contributing) with your opinion and where you see this being valuable as a standard*

## Private Discovery (API-Based)
There will undoubtably be private "agent stores" or proprietary agents where cards are exchanged behind custom APIs.

*We **are not** considering private discovery APIs as an A2A concern - please drop us a [note](https://github.com/google/A2A/blob/main/README.md#contributing) with your opinion and where you see this being valuable as a standard*

## Securing Agent Cards

Agent cards may contain sensitive information. Implementors may decide to secure their agent cards behind controls that require authentication and authorization. For example, within an organization, even an open discovery at a well-known path could be guarded by mTLS and restricted to specific clients. Registries and Private Discovery APIs should require authentication and return different artifacts for different identities. 

Note that implementors may include credential information (such as API Keys) in their Agent Cards. It is recommended that this information is NEVER available without Authentication. 
