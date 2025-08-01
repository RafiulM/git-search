'use client';

import { useState } from 'react';
import React from 'react';
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  File,
  Image as ImageIcon,
  Music,
  Video,
  Archive,
  Lock,
  Wrench,
  CodeIcon,
  Settings,
  FileText
} from 'lucide-react';

// Tree node interface
interface TreeNode {
  name: string;
  isDirectory: boolean;
  children?: TreeNode[];
  level: number;
}

// File type detection utility
const getFileIcon = (fileName: string, isDirectory: boolean = false) => {
  if (isDirectory) {
    return <Folder className="w-4 h-4 text-blue-500" />;
  }

  const extension = fileName.toLowerCase().split('.').pop();
  const iconProps = { className: "w-4 h-4" };

  switch (extension) {
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx':
    case 'vue':
    case 'svelte':
      return <CodeIcon {...iconProps} className="w-4 h-4 text-yellow-500" />;
    case 'py':
    case 'rb':
    case 'php':
    case 'java':
    case 'cpp':
    case 'c':
    case 'cs':
    case 'go':
    case 'rs':
      return <CodeIcon {...iconProps} className="w-4 h-4 text-green-500" />;
    case 'html':
    case 'htm':
    case 'xml':
      return <CodeIcon {...iconProps} className="w-4 h-4 text-orange-500" />;
    case 'css':
    case 'scss':
    case 'sass':
    case 'less':
      return <CodeIcon {...iconProps} className="w-4 h-4 text-blue-500" />;
    case 'json':
    case 'yaml':
    case 'yml':
    case 'toml':
    case 'ini':
      return <Settings {...iconProps} className="w-4 h-4 text-purple-500" />;
    case 'md':
    case 'mdx':
    case 'txt':
    case 'rtf':
      return <FileText {...iconProps} className="w-4 h-4 text-gray-500" />;
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'svg':
    case 'webp':
    case 'ico':
      return <ImageIcon {...iconProps} className="w-4 h-4 text-pink-500" />;
    case 'mp3':
    case 'wav':
    case 'flac':
    case 'aac':
      return <Music {...iconProps} className="w-4 h-4 text-purple-500" />;
    case 'mp4':
    case 'avi':
    case 'mov':
    case 'wmv':
    case 'flv':
      return <Video {...iconProps} className="w-4 h-4 text-red-500" />;
    case 'zip':
    case 'rar':
    case '7z':
    case 'tar':
    case 'gz':
      return <Archive {...iconProps} className="w-4 h-4 text-brown-500" />;
    case 'env':
    case 'key':
    case 'pem':
    case 'cert':
      return <Lock {...iconProps} className="w-4 h-4 text-red-600" />;
    case 'lock':
      return <Lock {...iconProps} className="w-4 h-4 text-gray-600" />;
    case 'config':
    case 'conf':
    case 'cfg':
      return <Wrench {...iconProps} className="w-4 h-4 text-gray-500" />;
    default:
      return <File {...iconProps} className="w-4 h-4 text-gray-400" />;
  }
};

// Parse tree structure string into tree nodes
const parseTreeStructure = (treeStr: string): TreeNode[] => {
  const lines = treeStr.split('\n').filter(line => line.trim());
  const nodes: TreeNode[] = [];
  const stack: { node: TreeNode; level: number }[] = [];

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) return;

    // Multiple approaches to extract clean name and level
    let cleanName = '';
    let level = 0;

    // Method 1: Count tree drawing characters for level
    const treeChars = line.match(/[├└│]/g);
    if (treeChars) {
      level = treeChars.length - 1;
      // Remove tree drawing characters
      cleanName = trimmed
        .replace(/^[├└│\s─┌┐┘┴┬┤┼╭╮╯╰╱╲╳]+/, '')
        .replace(/^[-─]+\s*/, '')
        .trim();
    } else {
      // Method 2: Use indentation
      const leadingSpaces = line.length - line.trimStart().length;
      level = Math.max(0, Math.floor(leadingSpaces / 2)); // More conservative level calculation
      cleanName = trimmed;
    }

    // Method 3: Handle simple list format (fallback)
    if (!cleanName && trimmed) {
      cleanName = trimmed;
      level = 0;
    }

    if (!cleanName) return;

    // Enhanced directory detection
    const lowerName = cleanName.toLowerCase();
    const isDirectory = 
      cleanName.endsWith('/') || 
      cleanName.endsWith(':') ||
      !cleanName.includes('.') ||
      // Common directory patterns
      ['src', 'lib', 'components', 'pages', 'utils', 'hooks', 'styles', 
       'public', 'assets', 'images', 'docs', 'test', 'tests', '__tests__',
       'node_modules', '.git', '.next', 'build', 'dist', 'out', 'bin',
       'scripts', 'config', 'configs', 'app', 'apps', 'packages',
       'modules', 'views', 'controllers', 'models', 'middleware',
       'routes', 'api', 'server', 'client', 'shared', 'common'].includes(lowerName) ||
      // Pattern matching for common directory structures
      /^[a-zA-Z0-9_-]+$/.test(cleanName) && !cleanName.includes('.');

    const node: TreeNode = {
      name: cleanName.replace(/[\/:]$/, ''), // Remove trailing / or :
      isDirectory,
      children: isDirectory ? [] : undefined,
      level
    };

    // Build hierarchy using stack
    while (stack.length > 0 && stack[stack.length - 1].level >= level) {
      stack.pop();
    }

    if (stack.length === 0) {
      // Root level
      nodes.push(node);
    } else {
      // Add as child to current parent
      const parent = stack[stack.length - 1].node;
      if (parent.children && parent.isDirectory) {
        parent.children.push(node);
      } else {
        // Fallback: add as root if parent structure is broken
        nodes.push(node);
      }
    }

    // Add directories to stack for potential children
    if (isDirectory) {
      stack.push({ node, level });
    }
  });

  return nodes;
};

// Tree Node Component
const TreeNodeComponent = ({ node, level = 0 }: { node: TreeNode; level?: number }) => {
  const [isExpanded, setIsExpanded] = useState(level < 2); // Auto-expand first 2 levels

  const toggleExpanded = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (node.isDirectory) {
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <div className="select-none">
      <div
        className={`flex items-center gap-2 py-1 px-2 hover:bg-muted/50 rounded transition-colors ${
          node.isDirectory ? 'cursor-pointer font-medium' : 'cursor-default'
        }`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={node.isDirectory ? toggleExpanded : undefined}
      >
        {node.isDirectory ? (
          <div className="flex-shrink-0">
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors" />
            )}
          </div>
        ) : (
          <div className="w-4" />
        )}
        
        <div className="flex-shrink-0">
          {node.isDirectory && isExpanded ? (
            <FolderOpen className="w-4 h-4 text-blue-500" />
          ) : (
            getFileIcon(node.name, node.isDirectory)
          )}
        </div>
        
        <span className="text-sm truncate" title={node.name}>
          {node.name}
          {node.isDirectory && node.children && node.children.length > 0 && (
            <span className="text-xs text-muted-foreground ml-1">
              ({node.children.length})
            </span>
          )}
        </span>
      </div>
      
      {node.isDirectory && isExpanded && node.children && node.children.length > 0 && (
        <div className="border-l border-muted ml-2">
          {node.children.map((child, index) => (
            <TreeNodeComponent 
              key={`${child.name}-${index}-${level}`} 
              node={child} 
              level={level + 1} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Main Tree Structure Component
export const RepositoryTree = ({ treeString }: { treeString: string }) => {
  const treeNodes = parseTreeStructure(treeString);

  // Debug logging to help troubleshoot
  if (process.env.NODE_ENV === 'development') {
    console.log('Raw tree string:', treeString.substring(0, 500) + '...');
    console.log('Parsed tree nodes:', treeNodes);
  }

  return (
    <div className="max-h-96 overflow-y-auto border rounded-lg bg-muted/20">
      {treeNodes.length > 0 ? (
        <div className="p-2">
          {treeNodes.map((node, index) => (
            <TreeNodeComponent key={`${node.name}-${index}-${node.level}`} node={node} />
          ))}
        </div>
      ) : (
        <div className="p-8 text-center text-muted-foreground">
          No files found in tree structure
        </div>
      )}
    </div>
  );
};