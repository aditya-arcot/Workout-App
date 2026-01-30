import { AdminService } from '@/api/generated'
import { AccessRequestStatusSchema } from '@/api/generated/schemas.gen'
import type {
    AccessRequestPublic,
    AccessRequestStatus,
} from '@/api/generated/types.gen'
import { zAccessRequestPublic } from '@/api/generated/zod.gen'
import { DataTable } from '@/components/data-table/DataTable'
import { DataTableColumnHeader } from '@/components/data-table/DataTableColumnHeader'
import { DataTableInlineRowActions } from '@/components/data-table/DataTableInlineRowActions'
import { createSelectColumn } from '@/components/data-table/DataTableSelectColumn'
import { Badge } from '@/components/ui/badge'
import { isHttpError, isHttpValidationError } from '@/lib/http'
import { notify } from '@/lib/notify'
import {
    blueBadgeClassName,
    greenBadgeClassName,
    redBadgeClassName,
} from '@/lib/styles'
import type {
    DataTableRowActionsConfig,
    DataTableToolbarConfig,
    FilterOption,
} from '@/models/data-table'
import type { ColumnDef } from '@tanstack/react-table'
import { Check, X } from 'lucide-react'
import { useState } from 'react'

function StatusBadge({ status }: { status: AccessRequestStatus }) {
    switch (status) {
        case 'pending':
            return <Badge className={blueBadgeClassName}>Pending</Badge>
        case 'approved':
            return <Badge className={greenBadgeClassName}>Approved</Badge>
        case 'rejected':
            return <Badge className={redBadgeClassName}>Rejected</Badge>
    }
}

function getStatusFilterOptions(): FilterOption[] {
    return AccessRequestStatusSchema.enum.map((status) => ({
        label: status.charAt(0).toUpperCase() + status.slice(1),
        value: status,
    }))
}

interface AccessRequestsTableProps {
    requests: AccessRequestPublic[]
    isLoading: boolean
    onRequestUpdated: (request: AccessRequestPublic) => void
}

export function AccessRequestsTable({
    requests,
    isLoading,
    onRequestUpdated,
}: AccessRequestsTableProps) {
    const [loadingRequestIds, setLoadingRequestIds] = useState<Set<number>>(
        new Set()
    )

    const handleUpdateStatus = async (
        request: AccessRequestPublic,
        status: 'approved' | 'rejected'
    ) => {
        setLoadingRequestIds((prev) => new Set(prev).add(request.id))
        try {
            const { error } = await AdminService.updateAccessRequestStatus({
                path: {
                    access_request_id: request.id,
                },
                body: {
                    status: status,
                },
            })
            if (error) {
                // TODO refresh stale data?
                if (isHttpError(error)) {
                    notify.error(error.detail)
                } else if (isHttpValidationError(error)) {
                    error.detail?.forEach((detail) => {
                        notify.error(`Validation error: ${detail.msg}`)
                    })
                } else {
                    notify.error('Failed to update access request status')
                }
                return
            }
            notify.success('Access request status updated')
            request.status = status
            onRequestUpdated(request)
        } finally {
            setLoadingRequestIds((prev) => {
                const next = new Set(prev)
                next.delete(request.id)
                return next
            })
        }
    }

    const rowActionsConfig: DataTableRowActionsConfig<AccessRequestPublic> = {
        schema: zAccessRequestPublic,
        menuItems: (row) => {
            if (row.status !== 'pending') return []

            // TODO confirm approve/reject
            const isRowLoading = loadingRequestIds.has(row.id)
            return [
                {
                    type: 'action',
                    label: 'Approve',
                    className: 'text-green-700',
                    icon: Check,
                    onSelect: () => handleUpdateStatus(row, 'approved'),
                    disabled: isRowLoading,
                },
                {
                    type: 'action',
                    className: 'text-red-700',
                    label: 'Reject',
                    icon: X,
                    onSelect: () => handleUpdateStatus(row, 'rejected'),
                    disabled: isRowLoading,
                },
            ]
        },
    }

    const columns: ColumnDef<AccessRequestPublic>[] = [
        createSelectColumn<AccessRequestPublic>(),
        {
            id: 'name',
            accessorFn: (row) => `${row.first_name} ${row.last_name}`,
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Name" />
            ),
            enableHiding: false,
        },
        {
            accessorKey: 'email',
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Email" />
            ),
            enableHiding: false,
        },
        {
            accessorKey: 'status',
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Status" />
            ),
            cell: ({ row }) => {
                return (
                    <div className="-ml-2">
                        <StatusBadge status={row.original.status} />
                    </div>
                )
            },
            filterFn: (row, id, value: string[]) => {
                return value.includes(row.getValue(id))
            },
            enableHiding: false,
        },
        {
            accessorKey: 'reviewer.username',
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Reviewed By" />
            ),
            cell: ({ row }) =>
                row.original.reviewer ? row.original.reviewer.username : '—',
            enableHiding: false,
        },
        {
            accessorKey: 'reviewed_at',
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Reviewed At" />
            ),
            cell: ({ row }) =>
                row.original.reviewed_at
                    ? new Date(row.original.reviewed_at).toLocaleString()
                    : '—',
            enableHiding: false,
        },
        {
            accessorKey: 'updated_at',
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Updated At" />
            ),
            cell: ({ row }) =>
                new Date(row.original.updated_at).toLocaleString(),
            enableHiding: false,
        },
        {
            id: 'actions',
            header: ({ column }) => (
                <DataTableColumnHeader
                    column={column}
                    title="Actions"
                    className="justify-center"
                />
            ),
            cell: ({ row }) => {
                const menuItems = rowActionsConfig.menuItems(row.original)
                return menuItems.length > 0 ? (
                    <DataTableInlineRowActions
                        row={row}
                        config={rowActionsConfig}
                    />
                ) : (
                    <div className="text-center">—</div>
                )
            },
            enableHiding: false,
        },
    ]

    const toolbarConfig: DataTableToolbarConfig = {
        search: {
            columnId: 'name',
            placeholder: 'Filter by name...',
        },
        filters: [
            {
                columnId: 'status',
                title: 'Status',
                options: getStatusFilterOptions(),
            },
        ],
        showViewOptions: false,
    }

    return (
        <DataTable
            data={requests}
            columns={columns}
            pageSize={5}
            isLoading={isLoading}
            toolbarConfig={toolbarConfig}
        />
    )
}
