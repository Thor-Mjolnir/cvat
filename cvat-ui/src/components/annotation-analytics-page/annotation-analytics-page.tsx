// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router';
import { Row, Col } from 'antd/lib/grid';
import Text from 'antd/lib/typography/Text';
import Alert from 'antd/lib/alert';
import Empty from 'antd/lib/empty';
import { getCore } from 'cvat-core-wrapper';
import GoBackButton from 'components/common/go-back-button';
import CVATLoadingSpinner from 'components/common/loading-spinner';
import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const core = getCore();

interface AnnotationCountData {
    label_id: number;
    label_name: string;
    count: number;
}

function AnnotationAnalyticsPage(): JSX.Element {
    const { tid } = useParams<{ tid: string }>();
    const [fetching, setFetching] = useState(true);
    const [data, setData] = useState<AnnotationCountData[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        setFetching(true);
        setError(null);
        
        core.server.request(`/api/test/tasks/${tid}/annotation-counts`, {
            method: 'GET',
        }).then((response: { data: AnnotationCountData[] }) => {
            if (isMounted) {
                setData(response.data);
                setFetching(false);
            }
        }).catch((err: Error) => {
            if (isMounted) {
                setError(err.message || 'An error occurred while fetching annotation counts.');
                setFetching(false);
            }
        });

        return () => {
            isMounted = false;
        };
    }, [tid]);

    const renderContent = (): JSX.Element => {
        if (fetching) {
            return <CVATLoadingSpinner />;
        }

        if (error) {
            return <Alert message="Failed to load analytics" description={error} type="error" showIcon />;
        }

        const totalAnnotations = data.reduce((sum, item) => sum + item.count, 0);
        if (!data || data.length === 0 || totalAnnotations === 0) {
            return <Empty description="No annotation data found for this task." />;
        }

        const chartData = {
            labels: data.map((d) => d.label_name),
            datasets: [
                {
                    label: 'Annotation Counts',
                    data: data.map((d) => d.count),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                },
            ],
        };

        const chartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top' as const,
                },
                title: {
                    display: true,
                    text: 'Annotation Counts by Class',
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                    },
                },
            },
        };

        return (
            <div style={{ padding: '20px', background: '#fff', borderRadius: '4px', marginTop: '20px' }}>
                <Bar data={chartData} options={chartOptions} />
            </div>
        );
    };

    return (
        <div className="cvat-annotation-analytics-page" style={{ height: '100%', overflow: 'auto', padding: '16px' }}>
            <Row justify="center">
                <Col span={22} xl={18} xxl={14} className="cvat-task-top-bar" style={{ marginBottom: '16px' }}>
                    <GoBackButton />
                </Col>
            </Row>
            <Row justify="center">
                <Col span={22} xl={18} xxl={14}>
                    <Text strong style={{ fontSize: '24px' }}>Annotation Analytics</Text>
                    {renderContent()}
                </Col>
            </Row>
        </div>
    );
}

export default React.memo(AnnotationAnalyticsPage);
